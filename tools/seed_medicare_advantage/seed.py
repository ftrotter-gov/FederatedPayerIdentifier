#!/usr/bin/env python3
"""Reads two CMS Medicare Advantage CSV files and generates one well-known payer JSON file per contract ID."""

import csv
import json
import os
import re
import sys

# Locate the source data and output directories relative to this script's location.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))

PAYER_URL_FILE = os.path.join(SCRIPT_DIR, "source_data", "payer_url_list.csv")
PLAN_CROSSWALK_FILE = os.path.join(SCRIPT_DIR, "source_data", "PlanCrosswalk2026_10012025.csv")
OUTPUT_BASE_DIR = os.path.join(REPO_ROOT, "payer_index_files", "medicare_advantage")

# Import the shared FPI generation library from the tools directory.
TOOLS_DIR = os.path.join(REPO_ROOT, "tools")
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)
from FPI_maker_cli import generate_fpi  # noqa: E402

# FHIR system URI strings used in the identifier and plan_identifiers blocks.
SYSTEM_FPI = "http://hl7.org/fhir/us/fast-ndh/StructureDefinition/FederatedPayerIdentifier"
SYSTEM_MEDICARE_PAYER = "http://hl7.org/fhir/us/fast-ndh/NotSure/WhatGoesHere/MedicarePayerIdentifer"
SYSTEM_MEDICARE_PLAN = "http://hl7.org/fhir/us/fast-ndh/NotSure/WhatGoesHere/MedicarePlanIdentifer"
RESOURCE_TYPE = "http://hl7.org/fhir/us/fast-ndh/StructureDefinition/NDHPayerWellknownDefinition"

# The only endpoint type extractable from this data source.
ENDPOINT_KEY = "davinci_pdex_provider_directory_endpoint#1.1"


def safe_name(name):
    """Convert a payer name to a lowercase, underscore-separated, special-character-free directory name."""
    name = name.lower().replace(" ", "_")
    name = re.sub(r"[^a-z0-9_]", "", name)
    name = re.sub(r"_+", "_", name).strip("_")
    return name


def parse_contract_id_field(field_value):
    """Split the combined 'H0028 - PAYER NAME' field into separate contract_id and payer_name strings."""
    parts = field_value.split(" - ", 1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return None, None


def load_payer_urls(filepath):
    """Read the payer URL CSV and return a dict of contract_id -> {payer_name, url}, skipping unusable rows."""
    payers = {}
    stats = {
        "total": 0,
        "skipped_machine_readable": 0,
        "skipped_empty_url": 0,
        "skipped_multi_url": 0,
        "processed": 0,
    }

    with open(filepath, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            stats["total"] += 1

            response_format = row.get("Response Format", "").strip()
            url = row.get("URL", "").strip()
            contract_id_field = row.get("Contract ID", "").strip()

            # Machine-readable JSON rows have a different format and are excluded per spec.
            if response_format.lower() == "machine-readable json":
                stats["skipped_machine_readable"] += 1
                continue

            # Rows with no URL provide nothing useful.
            if not url:
                stats["skipped_empty_url"] += 1
                continue

            # Rows with multiple space-separated URLs are skipped until a multi-URL strategy is defined.
            if " " in url:
                stats["skipped_multi_url"] += 1
                continue

            contract_id, payer_name = parse_contract_id_field(contract_id_field)
            if not contract_id:
                stats["skipped_empty_url"] += 1
                continue

            payers[contract_id] = {"payer_name": payer_name, "url": url}
            stats["processed"] += 1

    return payers, stats


def load_plan_crosswalk(filepath):
    """Read the plan crosswalk CSV and return a dict of contract_id -> list of unique {plan_id, plan_name} entries."""
    crosswalk = {}
    seen = set()  # Tracks (contract_id, plan_id, plan_name) tuples to prevent duplicate plan entries.

    with open(filepath, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            contract_id = row.get("CURRENT_CONTRACT_ID", "").strip()
            plan_id = row.get("CURRENT_PLAN_ID", "").strip()
            plan_name = row.get("CURRENT_PLAN_NAME", "").strip()

            if not contract_id:
                continue

            # The crosswalk contains both previous and current year rows, so the same plan can appear more than once.
            dedup_key = (contract_id, plan_id, plan_name)
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            if contract_id not in crosswalk:
                crosswalk[contract_id] = []

            crosswalk[contract_id].append({"plan_id": plan_id, "plan_name": plan_name})

    return crosswalk


def build_well_known_json(contract_id, payer_name, url, plans):
    """Construct the well-known payer JSON document for one contract, grouping all its plans under a single endpoint."""
    fpi = generate_fpi("CMS_CONTRACT_ID", contract_id)

    # Build one plan_identifier entry per plan, omitting plan_name when it is blank.
    plan_identifiers = []
    for plan in plans:
        entry = {"system": SYSTEM_MEDICARE_PLAN, "value": plan["plan_id"]}
        if plan["plan_name"]:
            entry["plan_name"] = plan["plan_name"]
        plan_identifiers.append(entry)

    # All plans under a single contract share the same URL, so one plan_group covers them all.
    plan_groups = []
    if plan_identifiers or url:
        plan_groups.append({
            "plan_identifiers": plan_identifiers,
            "plan_endpoints": {ENDPOINT_KEY: url},
        })

    doc = {
        "copied_from_url": None,
        "resourceType": RESOURCE_TYPE,
        "payerLegalName": payer_name,
        "identifier": [
            {"system": SYSTEM_FPI, "value": fpi},
            {"system": SYSTEM_MEDICARE_PAYER, "value": contract_id},
        ],
        "plan_groups": plan_groups,
    }

    return doc, fpi


# The complete set of top-level keys the seed writes.
SEED_TOP_LEVEL_KEYS = {"copied_from_url", "resourceType", "payerLegalName", "identifier", "plan_groups"}

# Keys the seed writes inside each plan_identifier entry.
SEED_PLAN_IDENTIFIER_KEYS = {"system", "value", "plan_name"}

# Keys the seed writes inside each plan_group entry.
SEED_PLAN_GROUP_KEYS = {"plan_identifiers", "plan_endpoints"}

# Keys the seed writes inside each identifier entry.
SEED_IDENTIFIER_KEYS = {"system", "value"}

# Endpoint keys the seed ever writes (one per plan_group).
SEED_ENDPOINT_KEYS = {ENDPOINT_KEY}


def collect_extra_fields(existing_doc, seed_doc):
    """Return a list of human-readable descriptions of any fields present in existing_doc
    that go beyond what the seed would produce (seed_doc is used only to identify the
    seed-generated endpoint key for that contract)."""
    extras = []

    # --- Top-level keys ---
    for key in existing_doc:
        if key not in SEED_TOP_LEVEL_KEYS:
            extras.append(f"top-level key '{key}'")

    # --- identifier entries ---
    for i, id_entry in enumerate(existing_doc.get("identifier", [])):
        for key in id_entry:
            if key not in SEED_IDENTIFIER_KEYS:
                extras.append(f"identifier[{i}] key '{key}'")

    # --- plan_groups ---
    for gi, group in enumerate(existing_doc.get("plan_groups", [])):
        for key in group:
            if key not in SEED_PLAN_GROUP_KEYS:
                extras.append(f"plan_groups[{gi}] key '{key}'")

        # plan_identifiers entries
        for pi, plan_id_entry in enumerate(group.get("plan_identifiers", [])):
            for key in plan_id_entry:
                if key not in SEED_PLAN_IDENTIFIER_KEYS:
                    extras.append(f"plan_groups[{gi}].plan_identifiers[{pi}] key '{key}'")

        # plan_endpoints keys
        for ep_key in group.get("plan_endpoints", {}):
            if ep_key not in SEED_ENDPOINT_KEYS:
                extras.append(f"plan_groups[{gi}].plan_endpoints key '{ep_key}'")

    return extras


def write_output_file(doc, payer_name, fpi):
    """Write the well-known JSON document to the appropriate subdirectory under payer_index_files/medicare_advantage/.

    If the target file already exists and contains fields beyond what the seed produces,
    it has been enriched beyond the seed data and will NOT be overwritten.  A warning is
    printed and the function returns (filepath, skipped=True).
    """
    dir_name = safe_name(payer_name)
    output_dir = os.path.join(OUTPUT_BASE_DIR, dir_name)
    os.makedirs(output_dir, exist_ok=True)

    filename = f"{dir_name}_{fpi}.well_known_payer.json"
    filepath = os.path.join(output_dir, filename)

    # Guard: if the file exists, check whether it has grown beyond the seed.
    if os.path.exists(filepath):
        try:
            with open(filepath, encoding="utf-8") as f:
                existing_doc = json.load(f)
            extra_fields = collect_extra_fields(existing_doc, doc)
            if extra_fields:
                print(f"    !! SKIPPED (file has grown beyond seed data):")
                for field in extra_fields:
                    print(f"       + {field}")
                return filepath, True
        except (json.JSONDecodeError, OSError) as exc:
            print(f"    !! WARNING: Could not read existing file for comparison ({exc}). Overwriting.")

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)
        f.write("\n")

    return filepath, False


def main():
    print("=" * 60)
    print("Medicare Advantage Well-Known JSON Seed Generator")
    print("=" * 60)

    print(f"\nLoading payer URL list from:\n  {PAYER_URL_FILE}")
    payers, url_stats = load_payer_urls(PAYER_URL_FILE)

    print(f"\nLoading plan crosswalk from:\n  {PLAN_CROSSWALK_FILE}")
    crosswalk = load_plan_crosswalk(PLAN_CROSSWALK_FILE)

    print(f"\nOutput directory:\n  {OUTPUT_BASE_DIR}")
    print()

    files_written = 0
    files_skipped_enriched = 0
    contracts_no_plans = 0

    for contract_id, payer_info in sorted(payers.items()):
        payer_name = payer_info["payer_name"]
        url = payer_info["url"]

        plans = crosswalk.get(contract_id, [])

        # Contracts with no matching crosswalk plans cannot produce a meaningful well-known file.
        if not plans:
            contracts_no_plans += 1
            print(f"  [{contract_id}] {payer_name}  -- SKIPPED (no crosswalk plans)")
            continue

        doc, fpi = build_well_known_json(contract_id, payer_name, url, plans)
        filepath, skipped = write_output_file(doc, payer_name, fpi)

        print(f"  [{contract_id}] {payer_name}")
        print(f"    -> {os.path.relpath(filepath, REPO_ROOT)}")

        if skipped:
            files_skipped_enriched += 1
            print(f"       Plans: {len(plans)}, FPI: {fpi}  [NOT overwritten — enriched beyond seed]")
        else:
            files_written += 1
            print(f"       Plans: {len(plans)}, FPI: {fpi}")

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Total rows in payer URL list:          {url_stats['total']}")
    print(f"  Skipped (machine-readable JSON):       {url_stats['skipped_machine_readable']}")
    print(f"  Skipped (empty URL):                   {url_stats['skipped_empty_url']}")
    print(f"  Skipped (multiple URLs):               {url_stats['skipped_multi_url']}")
    print(f"  Processed contract IDs:                {url_stats['processed']}")
    print(f"  Contracts with no crosswalk plans:     {contracts_no_plans}")
    print(f"  Well-known JSON files written:         {files_written}")
    print(f"  Skipped (enriched beyond seed data):   {files_skipped_enriched}")
    print()


if __name__ == "__main__":
    main()
