#!/usr/bin/env python3
"""
same_payer_different_plans_report.py

Scans all .well_known_payer.json files under payer_index_files/ and produces:

  1. reports/same_payer_different_plans_report.md
       Summary report with per-FPI plan-ID counts linked to detail pages,
       sorted by number of endpoint groups (descending).

  2. reports/per_fpi/<company_name>.md  (one per unique FPI)
       Detail page listing the well-known JSON file(s) for that FPI and every
       plan identifier organised by endpoint group.

KEY SEMANTICS (from WellKnownFileFormat.md and GeneratingFederatedPayerIdentifiers.md):
  - One FPI = one payer entity (the FPI is the authoritative identity).
  - One payer (FPI) CAN and SHOULD appear in multiple files when it has plans
    with different endpoint sets. Each file represents one distinct endpoint set
    for that payer. This is the intended design.
  - Plans that share the same endpoint set belong together in one plan_group
    within the same file.
  - "Same payer, different plans" = the same FPI appears in more than one file
    (each file = a different endpoint configuration = a different plan group).
  - If every FPI appears in exactly one file, it means all of that payer's plans
    share identical endpoints — which is fine, just not the multi-file case.

This script reports:
  1. FPIs that appear in more than one file (same payer, different endpoint sets)
  2. Distribution of file counts per FPI
  3. Total plan identifier counts per payer across all their files

Usage:
    python3 tools/same_payer_different_plans_report.py
"""

import json
import os
import re
from collections import defaultdict
from datetime import datetime

# ── Paths ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
PAYER_INDEX_ROOT = os.path.join(REPO_ROOT, "payer_index_files")
REPORTS_DIR = os.path.join(REPO_ROOT, "reports")
PER_FPI_DIR = os.path.join(REPORTS_DIR, "per_fpi")
REPORT_PATH = os.path.join(REPORTS_DIR, "same_payer_different_plans_report.md")

# Ensure output directories exist
os.makedirs(PER_FPI_DIR, exist_ok=True)


# ── Helper ─────────────────────────────────────────────────────────────────────
def slugify(name: str) -> str:
    """Convert a payer legal name to a filesystem-safe slug (lowercase, underscores)."""
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9]+", "_", slug)
    slug = slug.strip("_")
    return slug


# ── Collect all payer files ────────────────────────────────────────────────────
all_files = []
for root, dirs, files in os.walk(PAYER_INDEX_ROOT):
    for f in sorted(files):
        if f.endswith(".well_known_payer.json"):
            all_files.append(os.path.join(root, f))

all_files.sort()

# ── Parse each file ───────────────────────────────────────────────────────────
records = []
errors = []

for filepath in all_files:
    try:
        with open(filepath) as fh:
            data = json.load(fh)

        fpi = None
        other_ids = []
        for ident in data.get("identifier", []):
            system = ident.get("system", "")
            value = ident.get("value", "")
            if "FederatedPayerIdentifier" in system:
                fpi = value
            else:
                label = system.split("/")[-1] if "/" in system else system
                other_ids.append((label, value))

        # Retain full plan_groups structure (plan_identifiers + plan_endpoints together)
        raw_plan_groups = []
        plan_ids_flat = []
        for pg in data.get("plan_groups", []):
            plans = []
            for pi in pg.get("plan_identifiers", []):
                entry = {
                    "value": pi.get("value", ""),
                    "plan_name": pi.get("plan_name", ""),
                }
                plans.append(entry)
                plan_ids_flat.append(entry)
            endpoints = pg.get("plan_endpoints", {})
            raw_plan_groups.append({
                "plan_identifiers": plans,
                "plan_endpoints": endpoints,
            })

        rel = os.path.relpath(filepath, PAYER_INDEX_ROOT)
        category = rel.split(os.sep)[0]

        records.append({
            "filepath": filepath,
            "rel_file": rel,
            "filename": os.path.basename(filepath),
            "category": category,
            "legal_name": data.get("payerLegalName", "UNKNOWN"),
            "fpi": fpi,
            "other_ids": other_ids,
            "plan_ids": plan_ids_flat,
            "plan_group_count": len(raw_plan_groups),
            "raw_plan_groups": raw_plan_groups,
        })

    except Exception as e:
        errors.append((filepath, str(e)))

# ── Group files by FPI ─────────────────────────────────────────────────────────
by_fpi = defaultdict(list)
no_fpi_records = []
for rec in records:
    if rec["fpi"]:
        by_fpi[rec["fpi"]].append(rec)
    else:
        no_fpi_records.append(rec)

# ── Build payer summaries ──────────────────────────────────────────────────────
payer_summaries = []
for fpi, recs in by_fpi.items():
    all_plan_ids = []
    for r in recs:
        all_plan_ids.extend(r["plan_ids"])
    total_plan_groups = sum(r["plan_group_count"] for r in recs)
    legal_names = list({r["legal_name"] for r in recs})
    categories = sorted({r["category"] for r in recs})
    payer_summaries.append({
        "fpi": fpi,
        "legal_names": legal_names,
        "legal_name": legal_names[0],
        "slug": slugify(legal_names[0]),
        "num_files": len(recs),
        "num_plan_groups": total_plan_groups,
        "num_plans": len(all_plan_ids),
        "plan_ids": all_plan_ids,
        "files": recs,
        "categories": categories,
    })

# Sort: most endpoint groups first, then most plans, then by legal name
payer_summaries.sort(key=lambda x: (-x["num_plan_groups"], -x["num_plans"], x["legal_name"]))

# ── Partition: single-file vs multi-file payers ───────────────────────────────
multi_file_payers = [p for p in payer_summaries if p["num_files"] > 1]
single_file_payers = [p for p in payer_summaries if p["num_files"] == 1]

# Distribution of files per FPI
file_count_dist = defaultdict(int)
for p in payer_summaries:
    file_count_dist[p["num_files"]] += 1


# ── Generate per-FPI detail pages ─────────────────────────────────────────────
def write_per_fpi_report(p: dict) -> None:
    """Write reports/per_fpi/<slug>.md for a single payer summary."""
    slug = p["slug"]
    out_path = os.path.join(PER_FPI_DIR, f"{slug}.md")

    lines = []
    lines.append(f"# {p['legal_name']}")
    lines.append("")
    lines.append(f"**FPI:** `{p['fpi']}`")
    lines.append("")
    lines.append(f"**Category:** {', '.join(p['categories'])}")
    lines.append("")

    # ── Well-Known Import Files ────────────────────────────────────────────────
    lines.append("## Well-Known Payer Import Files")
    lines.append("")
    for r in p["files"]:
        # Relative path from reports/per_fpi/ to the JSON file
        rel_to_json = os.path.relpath(r["filepath"], PER_FPI_DIR)
        lines.append(f"- [{r['filename']}]({rel_to_json})")
    lines.append("")

    # ── Plan Groups ────────────────────────────────────────────────────────────
    # Collect all plan_groups across all files for this FPI, with file context
    all_groups = []
    for r in p["files"]:
        for pg in r["raw_plan_groups"]:
            all_groups.append({
                "source_file": r["filename"],
                "plan_identifiers": pg["plan_identifiers"],
                "plan_endpoints": pg["plan_endpoints"],
            })

    total_groups = len(all_groups)
    total_plans = p["num_plans"]

    lines.append(f"## Plan Groups ({total_groups} group{'s' if total_groups != 1 else ''}, {total_plans} plan{'s' if total_plans != 1 else ''} total)")
    lines.append("")

    for idx, grp in enumerate(all_groups, start=1):
        num_plans_in_grp = len(grp["plan_identifiers"])
        lines.append(f"### Plan Group {idx} of {total_groups}")
        lines.append("")

        # Source file (only useful when payer spans multiple files)
        if p["num_files"] > 1:
            lines.append(f"**Source file:** `{grp['source_file']}`")
            lines.append("")

        # Endpoints
        endpoints = grp["plan_endpoints"]
        if endpoints:
            lines.append("**Endpoints:**")
            lines.append("")
            lines.append("| Key | Value |")
            lines.append("|-----|-------|")
            for k, v in sorted(endpoints.items()):
                k_safe = str(k).replace("|", "\\|")
                v_safe = str(v).replace("|", "\\|")
                lines.append(f"| {k_safe} | {v_safe} |")
        else:
            lines.append("**Endpoints:** _(none specified)_")
        lines.append("")

        # Plans in this group
        lines.append(f"**Plans ({num_plans_in_grp}):**")
        lines.append("")
        if num_plans_in_grp == 0:
            lines.append("_No plan identifiers in this group._")
        else:
            lines.append("| Plan ID | Plan Name |")
            lines.append("|---------|-----------|")
            for pi in grp["plan_identifiers"]:
                plan_val = pi["value"].replace("|", "\\|")
                plan_name = pi["plan_name"].replace("|", "\\|")
                lines.append(f"| {plan_val} | {plan_name} |")
        lines.append("")

    with open(out_path, "w") as fh:
        fh.write("\n".join(lines) + "\n")


for p in payer_summaries:
    write_per_fpi_report(p)


# ── Build Markdown report ──────────────────────────────────────────────────────
lines = []

lines.append("# Same Payer, Different Plans — Report")
lines.append("")
lines.append(f"_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_")
lines.append("")
lines.append(
    "**Identity rule:** A payer is uniquely identified by its **Federated Payer Identifier (FPI)**. "
    "Directory names are for human convenience only. "
    "The same FPI appearing in **multiple files** is the intended design when a payer has plans "
    "with different endpoint sets — each file covers one distinct endpoint configuration. "
    "Plans sharing the same endpoint set belong in the same `plan_group` within a single file."
)
lines.append("")

# ── Summary ────────────────────────────────────────────────────────────────────
lines.append("## Summary")
lines.append("")
lines.append("| Metric | Count |")
lines.append("|--------|------:|")
lines.append(f"| Total payer files scanned | {len(all_files)} |")
lines.append(f"| Files successfully parsed | {len(records)} |")
lines.append(f"| Unique FPIs (distinct payers) | {len(by_fpi)} |")
lines.append(f"| **FPIs appearing in multiple files** (same payer, different endpoint sets) | **{len(multi_file_payers)}** |")
lines.append(f"| FPIs appearing in exactly one file | {len(single_file_payers)} |")
lines.append(f"| Files missing an FPI | {len(no_fpi_records)} |")
lines.append(f"| Parse errors | {len(errors)} |")
lines.append("")

# ── Distribution ───────────────────────────────────────────────────────────────
lines.append("## Distribution: Number of Files per FPI (Payer)")
lines.append("")
lines.append(
    "Each row shows how many payers (FPIs) have exactly N files. "
    "Payers with N > 1 are the 'same payer, different plans' cases."
)
lines.append("")
lines.append("| Files per FPI | # Payers | Notes |")
lines.append("|-------------:|---------:|-------|")
for n in sorted(file_count_dist.keys()):
    count = file_count_dist[n]
    note = "same payer, different endpoint sets ← target cases" if n > 1 else "all plans share the same endpoint set"
    lines.append(f"| {n} | {count} | {note} |")
lines.append("")

# ── Multi-file payers: the core "same payer, different plans" report ───────────
lines.append("## Same Payer, Different Plans (FPIs in Multiple Files)")
lines.append("")
if multi_file_payers:
    lines.append(
        f"**{len(multi_file_payers)} payer(s)** have their plans split across multiple files, "
        "each file covering a distinct endpoint configuration."
    )
    lines.append("")
    lines.append("| FPI | Payer Legal Name | # Files | # Endpoint Groups | # Plan IDs | Category |")
    lines.append("|-----|-----------------|--------:|----------------:|----------:|----------|")
    for p in multi_file_payers:
        plan_link = f"[{p['num_plans']}](per_fpi/{p['slug']}.md)"
        lines.append(
            f"| `{p['fpi']}` | {p['legal_name']} | {p['num_files']} "
            f"| {p['num_plan_groups']} | {plan_link} | {', '.join(p['categories'])} |"
        )
    lines.append("")
    lines.append("### Detailed Breakdown")
    lines.append("")
    for p in multi_file_payers:
        lines.append(f"#### {p['legal_name']}")
        lines.append(f"**FPI:** `{p['fpi']}`  |  **{p['num_files']} files** (distinct endpoint sets)")
        lines.append("")
        lines.append("| File | # Endpoint Groups | # Plan IDs |")
        lines.append("|------|----------------:|----------:|")
        for r in p["files"]:
            lines.append(
                f"| `{r['rel_file']}` | {r['plan_group_count']} | {len(r['plan_ids'])} |"
            )
        lines.append("")
else:
    lines.append(
        "_No FPI currently appears in more than one file. "
        "This means every payer's plans currently share identical endpoint sets "
        "(all plans are in a single file per payer). "
        "This is valid — it simply means no payer yet has plans requiring distinct endpoint configurations._"
    )
    lines.append("")

# ── Single-file payer summary ──────────────────────────────────────────────────
lines.append("## Single-File Payers (All Plans Share One Endpoint Set)")
lines.append("")
lines.append(
    f"These **{len(single_file_payers)} payers** each have exactly one file. "
    "Sorted by number of endpoint groups (descending), then plan count (descending)."
)
lines.append("")
lines.append("| FPI | Payer Legal Name | # Endpoint Groups | # Plan IDs | Category |")
lines.append("|-----|-----------------|----------------:|----------:|----------|")
# Already sorted by (-num_plan_groups, -num_plans, legal_name) from the global sort
for p in single_file_payers:
    plan_link = f"[{p['num_plans']}](per_fpi/{p['slug']}.md)"
    lines.append(
        f"| `{p['fpi']}` | {p['legal_name']} | {p['num_plan_groups']} "
        f"| {plan_link} | {', '.join(p['categories'])} |"
    )
lines.append("")

# ── Files missing FPI ──────────────────────────────────────────────────────────
if no_fpi_records:
    lines.append("## Files Missing an FPI")
    lines.append("")
    lines.append("These files have no Federated Payer Identifier and cannot be grouped by payer:")
    lines.append("")
    for r in no_fpi_records:
        lines.append(f"- `{r['rel_file']}` — {r['legal_name']}")
    lines.append("")

# ── Parse errors ───────────────────────────────────────────────────────────────
if errors:
    lines.append("## Parse Errors")
    lines.append("")
    for fp, err in errors:
        rel = os.path.relpath(fp, REPO_ROOT)
        lines.append(f"- `{rel}`: {err}")
    lines.append("")

# ── Write main report ──────────────────────────────────────────────────────────
with open(REPORT_PATH, "w") as fh:
    fh.write("\n".join(lines) + "\n")

print(f"Main report:      {os.path.relpath(REPORT_PATH, REPO_ROOT)}")
print(f"Per-FPI reports:  {os.path.relpath(PER_FPI_DIR, REPO_ROOT)}/ ({len(payer_summaries)} files)")
print(f"  Files scanned:                          {len(all_files)}")
print(f"  Unique FPIs (payers):                   {len(by_fpi)}")
print(f"  FPIs in multiple files (same payer,")
print(f"    different endpoint sets):              {len(multi_file_payers)}")
print(f"  FPIs in exactly one file:               {len(single_file_payers)}")
if no_fpi_records:
    print(f"  Files missing FPI:                      {len(no_fpi_records)}")
if errors:
    print(f"  Parse errors:                           {len(errors)}")
