#!/usr/bin/env python3
"""
same_payer_different_plans_report.py

Scans all .well_known_payer.json files under payer_index_files/ and produces
a Markdown report (same_payer_different_plans_report.md) in the repo root.

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
from collections import defaultdict
from datetime import datetime

# ── Paths ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
PAYER_INDEX_ROOT = os.path.join(REPO_ROOT, "payer_index_files")
REPORT_PATH = os.path.join(REPO_ROOT, "same_payer_different_plans_report.md")

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

        # Collect plan_identifiers and endpoint sets across all plan_groups
        plan_ids = []
        endpoint_sets = []
        for pg in data.get("plan_groups", []):
            for pi in pg.get("plan_identifiers", []):
                plan_ids.append({
                    "value": pi.get("value", ""),
                    "plan_name": pi.get("plan_name", ""),
                })
            eps = pg.get("plan_endpoints", {})
            endpoint_sets.append(frozenset(eps.items()))

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
            "plan_ids": plan_ids,
            "plan_group_count": len(data.get("plan_groups", [])),
            "endpoint_sets": endpoint_sets,
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
        "num_files": len(recs),
        "num_plan_groups": total_plan_groups,
        "num_plans": len(all_plan_ids),
        "plan_ids": all_plan_ids,
        "files": recs,
        "categories": categories,
    })

# Sort: payers with most files first, then by legal name
payer_summaries.sort(key=lambda x: (-x["num_files"], x["legal_name"]))

# ── Partition: single-file vs multi-file payers ───────────────────────────────
multi_file_payers = [p for p in payer_summaries if p["num_files"] > 1]
single_file_payers = [p for p in payer_summaries if p["num_files"] == 1]

# Distribution of files per FPI
file_count_dist = defaultdict(int)
for p in payer_summaries:
    file_count_dist[p["num_files"]] += 1

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
        lines.append(
            f"| `{p['fpi']}` | {p['legal_name']} | {p['num_files']} "
            f"| {p['num_plan_groups']} | {p['num_plans']} | {', '.join(p['categories'])} |"
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
    f"These **{len(single_file_payers)} payers** each have exactly one file, "
    "meaning all their plans currently share the same endpoint configuration."
)
lines.append("")
lines.append("| FPI | Payer Legal Name | # Endpoint Groups | # Plan IDs | Category |")
lines.append("|-----|-----------------|----------------:|----------:|----------|")
# Sort single-file payers by plan count descending
for p in sorted(single_file_payers, key=lambda x: -x["num_plans"]):
    lines.append(
        f"| `{p['fpi']}` | {p['legal_name']} | {p['num_plan_groups']} "
        f"| {p['num_plans']} | {', '.join(p['categories'])} |"  
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

# ── Write report ───────────────────────────────────────────────────────────────
with open(REPORT_PATH, "w") as fh:
    fh.write("\n".join(lines) + "\n")

print(f"Report written to: {REPORT_PATH}")
print(f"  Files scanned:                          {len(all_files)}")
print(f"  Unique FPIs (payers):                   {len(by_fpi)}")
print(f"  FPIs in multiple files (same payer,")
print(f"    different endpoint sets):              {len(multi_file_payers)}")
print(f"  FPIs in exactly one file:               {len(single_file_payers)}")
if no_fpi_records:
    print(f"  Files missing FPI:                      {len(no_fpi_records)}")
if errors:
    print(f"  Parse errors:                           {len(errors)}")
