#!/usr/bin/env python3
"""One-time migration for the Aetna Texas FPI mockup (AI_Instructions/AetnaTexasMockup.md).

For each of the four Aetna entities this script:
  1. Loads the existing seeded well-known payer file (named with the old
     legal-name-hash FPI uuid).
  2. Builds a new well-known file whose FPI is derived from a real payer
     identifier system (HIOS_ID, STATE_DOI_ID, NAIC_ID, or LEI), with the
     four-component FPI entry first in "identifier".
  3. Folds in all of the payer identifiers from
     mockup_data/aetna_texas_payer_identifiers.csv (with notes, lookup_url,
     and expiration metadata), including ALL "Texas Health + Aetna Health
     Plan Inc." rows into aetna_health_inc_tx.
  4. Adds payer_level_string_search_matches and sets is_seeded to false.
  5. Writes the new file (named with the new FPI uuid) and replaces the old
     file with a stub: {"is_seeded": false, "new_file": "<path to new file>"}.

Run from the repository root:
    python tools/apply_aetna_texas_mockup.py
"""

import csv
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from FPI_maker_cli import generate_fpi  # noqa: E402

BASE_DIR = os.path.join("payer_index_files", "medicare_advantage")
CSV_PATH = os.path.join("mockup_data", "aetna_texas_payer_identifiers.csv")
SYSTEM_URL_PREFIX = "https://directory.cms.gov/payer_identification_system/"

SYSTEM_URLS = {
    "NAIC_ID": SYSTEM_URL_PREFIX + "naic_id",
    "EIN": SYSTEM_URL_PREFIX + "ein",
    "STATE_DOI_ID": SYSTEM_URL_PREFIX + "state_doi_id",
    "HIOS_ID": SYSTEM_URL_PREFIX + "hios_id",
    "LEI": SYSTEM_URL_PREFIX + "lei",
    "CMS_CONTRACT_ID": SYSTEM_URL_PREFIX + "cms_contract_id",
    "X12_PAYER_ID": SYSTEM_URL_PREFIX + "x12_payer_id",
}

# The per-entity migration plan (approved in AI_Instructions/AetnaTexasMockup.md).
ENTITIES = {
    "Aetna Health Inc. (Texas)": {
        "dir_name": "aetna_health_inc_tx",
        "old_fpi": "6594b1a3-bfdb-5434-b228-09d9cdfa8c87",
        "fpi_source_system_id": "HIOS_ID",
        "fpi_source_value": "58840",
        "search_matches": [
            "Aetna",
            "Aetna Health",
            "Aetna Health Inc. (TX)",
            "Aetna Health Inc. (Texas)",
            "Texas Health + Aetna Health Plan Inc.",
            "Texas Health Aetna",
        ],
    },
    "Aetna Better Health of Texas, Inc.": {
        "dir_name": "aetna_better_health_of_texas_inc",
        "old_fpi": "e9a3ae68-5f89-594a-b281-6681770b34c2",
        "fpi_source_system_id": "STATE_DOI_ID",
        "fpi_source_value": "TX-68775",
        "search_matches": [
            "Aetna",
            "Aetna Better Health of Texas",
            "Aetna Better Health of Texas, Inc.",
        ],
    },
    "Aetna Health and Life Insurance Company": {
        "dir_name": "aetna_health_and_life_insurance_company",
        "old_fpi": "4c7be225-8325-5765-b861-a9ebdf004a50",
        "fpi_source_system_id": "NAIC_ID",
        "fpi_source_value": "78700",
        "search_matches": [
            "Aetna",
            "Aetna Health and Life Insurance",
            "Aetna Health and Life Insurance Company",
        ],
    },
    "Aetna Life Insurance Company": {
        "dir_name": "aetna_life_insurance_company",
        "old_fpi": "565a5151-8480-5330-8910-4dfe0dab0717",
        "fpi_source_system_id": "LEI",
        "fpi_source_value": "SPCOIWBJM0HFYQX3A364",
        "search_matches": [
            "Aetna",
            "Aetna Life Insurance",
            "Aetna Life Insurance Company",
        ],
    },
}


class AetnaTexasMockupMigration:
    """Namespace class holding the migration steps as static methods."""

    @staticmethod
    def _load_csv_rows_by_entity(*, csv_path):
        """Group the CSV identifier rows by target entity name.

        ALL "Texas Health + Aetna Health Plan Inc." rows fold into
        aetna_health_inc_tx per the approved instructions.  STATE_DOI_ID
        values receive the two-letter state prefix (all rows are Texas).
        """
        csv_name_to_entity = {entity_name: entity_name for entity_name in ENTITIES}
        csv_name_to_entity["Texas Health + Aetna Health Plan Inc."] = "Aetna Health Inc. (Texas)"

        entity_csv_rows = {entity_name: [] for entity_name in ENTITIES}
        with open(csv_path, encoding="utf-8", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                target_entity = csv_name_to_entity[row["payer_corporation"]]
                identifier_type = row["identifier_type"]
                identifier_value = row["identifier"]
                if identifier_type == "STATE_DOI_ID":
                    identifier_value = "TX-" + identifier_value
                entity_csv_rows[target_entity].append({
                    "system": SYSTEM_URLS[identifier_type],
                    "value": identifier_value,
                    "notes": row["notes"],
                    "lookup_url": row["lookup_url"],
                    "expiration": row["expiration"],
                })
        return entity_csv_rows

    @staticmethod
    def _build_identifier_list(*, entity, new_fpi, old_doc, csv_rows):
        """Build the new identifier list: four-component FPI entry first,
        then the pre-existing non-FPI identifiers (enriched with CSV metadata
        when they match), then the remaining CSV identifiers."""
        identifiers = [{
            "system": SYSTEM_URL_PREFIX + "fpi",
            "value": new_fpi,
            "fpi_source_system": SYSTEM_URLS[entity["fpi_source_system_id"]],
            "fpi_source_value": entity["fpi_source_value"],
        }]

        existing_non_fpi = [dict(entry) for entry in old_doc["identifier"][1:]]

        new_entries = []
        for csv_entry in csv_rows:
            merged = False
            for existing_entry in existing_non_fpi:
                if (existing_entry["system"] == csv_entry["system"]
                        and existing_entry["value"] == csv_entry["value"]):
                    existing_entry["notes"] = csv_entry["notes"]
                    existing_entry["lookup_url"] = csv_entry["lookup_url"]
                    existing_entry["expiration"] = csv_entry["expiration"]
                    merged = True
                    break
            if not merged:
                new_entries.append(csv_entry)

        identifiers.extend(existing_non_fpi)
        identifiers.extend(new_entries)
        return identifiers

    @staticmethod
    def _migrate_entity(*, entity_name, entity, csv_rows):
        """Write the new well-known file and replace the old one with a stub."""
        new_fpi = generate_fpi(
            system_id=entity["fpi_source_system_id"],
            payer_id_value=entity["fpi_source_value"],
        )

        entity_dir = os.path.join(BASE_DIR, entity["dir_name"])
        old_filename = f"{entity['dir_name']}_{entity['old_fpi']}.well_known_payer.json"
        new_filename = f"{entity['dir_name']}_{new_fpi}.well_known_payer.json"
        old_path = os.path.join(entity_dir, old_filename)
        new_path = os.path.join(entity_dir, new_filename)

        with open(old_path, encoding="utf-8") as old_file:
            old_doc = json.load(old_file)

        if "new_file" in old_doc:
            print(f"{entity_name}: SKIPPED — {old_path} is already a migration stub.")
            return

        identifiers = AetnaTexasMockupMigration._build_identifier_list(
            entity=entity, new_fpi=new_fpi, old_doc=old_doc, csv_rows=csv_rows
        )

        new_doc = {
            "copied_from_url": old_doc.get("copied_from_url"),
            "resourceType": old_doc["resourceType"],
            "payerLegalName": old_doc["payerLegalName"],
            "identifier": identifiers,
            "payer_level_string_search_matches": entity["search_matches"],
            "plan_groups": old_doc["plan_groups"],
            "is_seeded": False,
        }

        with open(new_path, "w", encoding="utf-8") as new_file:
            json.dump(new_doc, new_file, indent=2)
            new_file.write("\n")

        stub_doc = {
            "is_seeded": False,
            "new_file": new_path.replace(os.sep, "/"),
        }
        with open(old_path, "w", encoding="utf-8") as old_file:
            json.dump(stub_doc, old_file, indent=2)
            old_file.write("\n")

        print(f"{entity_name}:")
        print(f"  new  -> {new_path}  ({len(identifiers)} identifiers, FPI {new_fpi})")
        print(f"  stub -> {old_path}")

    @staticmethod
    def run():
        """Run the full migration for all four Aetna entities."""
        os.chdir(REPO_ROOT)
        entity_csv_rows = AetnaTexasMockupMigration._load_csv_rows_by_entity(csv_path=CSV_PATH)
        for entity_name, entity in ENTITIES.items():
            AetnaTexasMockupMigration._migrate_entity(
                entity_name=entity_name,
                entity=entity,
                csv_rows=entity_csv_rows[entity_name],
            )


if __name__ == "__main__":
    AetnaTexasMockupMigration.run()