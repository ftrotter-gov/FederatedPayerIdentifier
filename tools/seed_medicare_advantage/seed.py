#!/usr/bin/env python3
"""Reads two CMS Medicare Advantage CSV files and generates one well-known payer JSON file per contract ID."""

import csv
import json
import os
import re
import uuid

# Locate the source data and output directories relative to this script's location.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))

PAYER_URL_FILE = os.path.join(SCRIPT_DIR, "source_data", "payer_url_list.csv")
PLAN_CROSSWALK_FILE = os.path.join(SCRIPT_DIR, "source_data", "PlanCrosswalk2026_10012025.csv")
OUTPUT_BASE_DIR = os.path.join(REPO_ROOT, "payer_index_files", "medicare_advantage")

# Build the Medicare Advantage uuid5 namespace by chaining from NAMESPACE_DNS, as specified.
PARENT_NAMESPACE = uuid.NAMESPACE_DNS
MEDICARE_ADVANTAGE_SYSTEM_UUID = uuid.uuid5(PARENT_NAMESPACE, "CMS_CONTRACT_ID.fhir")

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


def generate_fpi(contract_id):
    """Generate a deterministic uuid5 Federated Payer Identifier from a Medicare contract ID."""
    return str(uuid.uuid5(MEDICARE_ADVANTAGE_SYSTEM_UUID, contract_id))


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
    fpi = generate_fpi(contract_id)

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


def write_output_file(doc, payer_name, fpi):
    """Write the well-known JSON document to the appropriate subdirectory under payer_index_files/medicare_advantage/."""
    dir_name = safe_name(payer_name)
    output_dir = os.path.join(OUTPUT_BASE_DIR, dir_name)
    os.makedirs(output_dir, exist_ok=True)

    filename = f"{dir_name}_{fpi}.well_known_payer.json"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)
        f.write("\n")

    return filepath


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
        filepath = write_output_file(doc, payer_name, fpi)
        files_written += 1
        print(f"  [{contract_id}] {payer_name}")
        print(f"    -> {os.path.relpath(filepath, REPO_ROOT)}")
        print(f"       Plans: {len(plans)}, FPI: {fpi}")

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Total rows in payer URL list:      {url_stats['total']}")
    print(f"  Skipped (machine-readable JSON):   {url_stats['skipped_machine_readable']}")
    print(f"  Skipped (empty URL):               {url_stats['skipped_empty_url']}")
    print(f"  Skipped (multiple URLs):           {url_stats['skipped_multi_url']}")
    print(f"  Processed contract IDs:            {url_stats['processed']}")
    print(f"  Contracts with no crosswalk plans: {contracts_no_plans}")
    print(f"  Well-known JSON files written:     {files_written}")
    print()


if __name__ == "__main__":
    main()
