#!/usr/bin/env python3
"""Migration/re-migration tool for the Aetna Texas FPI mockup (AI_Instructions/AetnaTexasMockup.md).

For each of the four Aetna entities this script:
  1. Loads the existing seeded well-known payer file (named with the current
     legal-name-hash FPI uuid, as produced by seed_medicare_advantage/seed.py).
  2. Builds a new well-known file whose FPI is derived from a real payer
     identifier system (HIOS_ID, STATE_DOI_ID, NAIC_ID, or LEI), with the
     four-component FPI entry first in "identifier".
  3. Folds in all of the payer identifiers from
     mockup_data/aetna_texas_payer_identifiers.csv (with notes, lookup_url,
     and expiration metadata), including ALL "Texas Health + Aetna Health
     Plan Inc." rows into aetna_health_inc_tx.
  4. Grafts the full Aetna FHIR endpoint set into every plan_group (all four
     entities share the same Aetna/CVS endpoint infrastructure).
  5. Adds payer_level_string_search_matches and sets is_seeded to false.
  6. Writes the new file (named with the new FPI uuid) and replaces the old
     seeded file with a stub: {"is_seeded": false, "new_file": "<path>"}.

This script is safe to re-run after a fresh seed cycle:
  - Delete curated + stub files from all four payer directories.
  - Run seed_medicare_advantage/seed.py to regenerate fresh seeded files.
  - Re-run this script to re-apply the Aetna Texas mockup curation.

Run from the repository root:
    python tools/apply_aetna_texas_mockup.py
"""

import csv
import json
import os
import re
import sys
import uuid

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

# All four Aetna Texas entities share the same Aetna/CVS FHIR endpoint
# infrastructure.  These endpoints were manually verified and added in commit
# 21f1baa.  They are grafted onto every plan_group produced by the seed so
# that a re-seed + re-migration preserves the manually curated endpoint data.
AETNA_PLAN_ENDPOINTS = {
    "davinci_crd_hook_endpoint#1.1": "https://apix.cvshealth.com/v1/cdshooks/cds-services/",
    "davinci_crd_hook_endpoint#1.2": None,
    "davinci_dtr_qpackage_endpoint#1.2": None,
    "davinci_pas_submission_endpoint#1.2": "https://apix.cvshealth.com/priorauthorizationsupport/v1/Claim/$submit",
    "davinci_cdex_attachsubmit_endpoint#2.1": "https://apix.cvshealth.com/clinicaldataexchange/v1/$submit-attachment",
    "davinci_pdex_provider_directory_endpoint#1.1": "https://apif1.aetna.com/fhir/v1/providerdirectorydata/",
    "davinci_pdex_provider_directory_endpoint_all_at_once#1.1": None,
    "davinci_provider_payer_access_endpoint#1.1": "https://apix.cvshealth.com/provideraccess/v1/",
    "davinci_payer_to_payer_endpoint#1.1": None,
    "carin_bluebutton_endpoint#1.0": "https://apif1.aetna.com/fhir/v3/patientaccess/",
    "carin_bluebutton_endpoint#1.0_uscore3.1": "https://apif1.aetna.com/fhir/v2/patientaccess/",
    "davinci_pdex_patient_endpoint#2.0": "https://apif1.aetna.com/fhir/v3/patientaccess/",
    "davinci_pdex_patient_endpoint#2.0_uscore3.1": "https://apif1.aetna.com/fhir/v2/patientaccess/",
    "carin_rtpbc_member_endpoint#1.0": "https://apif1.aetna.com/fhir/v1/realtimepharmacybenefitcheck/",
    "carin_rtpbc_provider_endpoint#1.0": "https://apix.cvshealth.com/realtimepharmacybenefitcheck/v1/",
    "davinci_pdex_formulary_endpoint#2.0": "https://apif1.aetna.com/fhir/v3/patientaccess/",
    "payer_homepage": "https://www.aetna.com/",
    "ndh_meta_fhir_signup_url": "https://developerportal.aetna.com/",
    "ndh_meta_documentation_url": "https://developerportal.aetna.com/fhirapiasegregation",
}

# The per-entity migration plan (approved in AI_Instructions/AetnaTexasMockup.md).
# "seed_fpi" is the LEGAL_NAME_HASH-derived FPI that seed.py writes into the
# seeded filename — this is what the script reads as its source document.
ENTITIES = {
    "Aetna Health Inc. (Texas)": {
        "dir_name": "aetna_health_inc_tx",
        "seed_fpi": "fbf6a17b-f8df-5772-9ddc-692b912af2b7",
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
        "seed_fpi": "b8010e50-6078-5f92-b303-db16d1ae5047",
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
        "seed_fpi": "e9928c4d-f9ca-5b5e-ba83-0d0d46099771",
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
        "seed_fpi": "72c771e1-464f-51d6-b6e3-1c2deaef5e50",
        "fpi_source_system_id": "LEI",
        "fpi_source_value": "SPCOIWBJM0HFYQX3A364",
        "search_matches": [
            "Aetna",
            "Aetna Life Insurance",
            "Aetna Life Insurance Company",
        ],
    },
}


def _safe_name(name):
    """Convert a payer name to a lowercase, underscore-separated, special-character-free string."""
    name = name.lower().replace(" ", "_")
    name = re.sub(r"[^a-z0-9_]", "", name)
    name = re.sub(r"_+", "_", name).strip("_")
    return name


class AetnaTexasMockupMigration:
    """Namespace class holding the migration steps as static methods."""

    @staticmethod
    def _load_csv_rows_by_entity(*, csv_path):
        """Read the CSV and return a dict: entity_name -> list of identifier dicts."""
        rows_by_entity = {name: [] for name in ENTITIES}
        rows_by_entity["Texas Health + Aetna Health Plan Inc."] = []

        with open(csv_path, encoding="utf-8", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                corp = row["payer_corporation"].strip()
                id_type = row["identifier_type"].strip()
                identifier = row["identifier"].strip()
                notes = row.get("notes", "").strip()
                lookup_url = row.get("lookup_url", "").strip()
                expiration = row.get("expiration", "").strip()

                if corp not in rows_by_entity:
                    continue
                system_url = SYSTEM_URLS.get(id_type)
                if not system_url:
                    continue
                entry = {
                    "system": system_url,
                    "value": identifier,
                    "notes": notes,
                    "lookup_url": lookup_url,
                    "expiration": expiration,
                }
                if id_type == "STATE_DOI_ID":
                    entry["value"] = f"TX-{identifier}"
                rows_by_entity[corp].append(entry)

        # Merge Texas Health rows into aetna_health_inc_tx per AetnaTexasMockup.md Q3.
        rows_by_entity["Aetna Health Inc. (Texas)"].extend(
            rows_by_entity.pop("Texas Health + Aetna Health Plan Inc.")
        )
        return rows_by_entity

    @staticmethod
    def _build_identifier_list(*, entity, new_fpi, seed_doc, csv_rows):
        """Merge the FPI entry, seed identifiers, and CSV rows into one list.

        Produces the new multi-FPI format (WellKnownFileFormat.md PR #1):
          - FPI entry: is_fpi=True, payerLegalName and payer_level_string_search_matches
            embedded inside it, fpi_source_system/value from the approved assignment.
          - Every non-FPI identifier: is_fpi=False, parent_fpi=new_fpi.
        """
        identifiers = [{
            "system": SYSTEM_URL_PREFIX + "fpi",
            "value": new_fpi,
            "is_fpi": True,
            # payerLegalName now lives inside the FPI identifier entry (new multi-FPI format).
            # The updated seed stores it there; pull it from the seed's FPI entry.
            "payerLegalName": seed_doc["identifier"][0]["payerLegalName"],
            "payer_level_string_search_matches": entity["search_matches"],
            "fpi_source_system": SYSTEM_URLS[entity["fpi_source_system_id"]],
            "fpi_source_value": entity["fpi_source_value"],
        }]

        # Carry forward all non-FPI identifiers from the seed (CMS_CONTRACT_IDs).
        # The seed sets is_fpi/parent_fpi on them, but parent_fpi still points at
        # the seed's LEGAL_NAME_HASH FPI.  Rewrite parent_fpi to the curated FPI.
        existing_non_fpi = []
        for entry in seed_doc["identifier"][1:]:
            updated = dict(entry)
            updated["is_fpi"] = False
            updated["parent_fpi"] = new_fpi
            existing_non_fpi.append(updated)

        new_entries = []
        for csv_entry in csv_rows:
            merged = False
            for existing_entry in existing_non_fpi:
                if (existing_entry["system"] == csv_entry["system"]
                        and existing_entry["value"] == csv_entry["value"]):
                    existing_entry["notes"] = csv_entry["notes"]
                    if csv_entry.get("lookup_url"):
                        existing_entry["lookup_url"] = csv_entry["lookup_url"]
                    existing_entry["expiration"] = csv_entry["expiration"]
                    merged = True
                    break
            if not merged:
                # New CSV-only entry: add is_fpi/parent_fpi to conform to the format.
                new_entry = dict(csv_entry)
                new_entry["is_fpi"] = False
                new_entry["parent_fpi"] = new_fpi
                new_entries.append(new_entry)

        identifiers.extend(existing_non_fpi)
        identifiers.extend(new_entries)
        return identifiers

    @staticmethod
    def _graft_endpoints_into_plan_groups(plan_groups, new_fpi):
        """Replace plan_endpoints with the full Aetna set; ensure parent_fpi and f_plan_id
        are set on every plan identifier (new multi-FPI format requirements).

        The seed already sets parent_fpi and f_plan_id on plan identifiers, but:
          - parent_fpi must now reference new_fpi (the curated FPI), not the old seed FPI.
          - f_plan_id is preserved from the seed output (a fresh random UUIDv4 per plan).
        """
        enriched = []
        for pg in plan_groups:
            new_pg = dict(pg)
            # Fix parent_fpi on every plan identifier to point at the curated FPI.
            updated_plan_ids = []
            for plan_id in pg.get("plan_identifiers", []):
                updated = dict(plan_id)
                updated["parent_fpi"] = new_fpi
                # Ensure f_plan_id exists (seed sets it; preserve it if already present).
                if "f_plan_id" not in updated:
                    updated["f_plan_id"] = str(uuid.uuid4())
                updated_plan_ids.append(updated)
            new_pg["plan_identifiers"] = updated_plan_ids
            new_pg["plan_endpoints"] = dict(AETNA_PLAN_ENDPOINTS)
            enriched.append(new_pg)
        return enriched

    @staticmethod
    def _find_seed_file(entity_dir, dir_name, seed_fpi):
        """Return the path to the seeded file for this entity, or None if not found."""
        canonical = os.path.join(entity_dir, f"{dir_name}_{seed_fpi}.well_known_payer.json")
        if os.path.exists(canonical):
            return canonical
        if os.path.isdir(entity_dir):
            for fname in sorted(os.listdir(entity_dir)):
                if not fname.endswith(".well_known_payer.json"):
                    continue
                fpath = os.path.join(entity_dir, fname)
                try:
                    with open(fpath, encoding="utf-8") as f:
                        doc = json.load(f)
                    if doc.get("is_seeded") is True:
                        return fpath
                except (json.JSONDecodeError, OSError):
                    continue
        return None

    @staticmethod
    def _migrate_entity(*, entity_name, entity, csv_rows):
        """Write the new curated well-known file and replace the seed file with a stub."""
        new_fpi = generate_fpi(
            system_id=entity["fpi_source_system_id"],
            payer_id_value=entity["fpi_source_value"],
        )

        entity_dir = os.path.join(BASE_DIR, entity["dir_name"])
        seed_path = AetnaTexasMockupMigration._find_seed_file(
            entity_dir=entity_dir,
            dir_name=entity["dir_name"],
            seed_fpi=entity["seed_fpi"],
        )
        new_filename = f"{entity['dir_name']}_{new_fpi}.well_known_payer.json"
        new_path = os.path.join(entity_dir, new_filename)

        if seed_path is None:
            print(f"{entity_name}: ERROR — no seeded file found in {entity_dir}.")
            print(f"  Run seed_medicare_advantage/seed.py first.")
            return

        with open(seed_path, encoding="utf-8") as f:
            seed_doc = json.load(f)

        if "new_file" in seed_doc or seed_doc.get("is_seeded") is not True:
            print(f"{entity_name}: ERROR — {seed_path} is not a valid seeded file.")
            print(f"  Delete all files in {entity_dir} and re-run seed.py first.")
            return

        identifiers = AetnaTexasMockupMigration._build_identifier_list(
            entity=entity, new_fpi=new_fpi, seed_doc=seed_doc, csv_rows=csv_rows
        )
        plan_groups = AetnaTexasMockupMigration._graft_endpoints_into_plan_groups(
            seed_doc["plan_groups"], new_fpi
        )

        # payerLegalName and payer_level_string_search_matches are now embedded
        # inside the FPI identifier entry (new multi-FPI format from PR #1).
        # They must NOT appear at the top level.
        new_doc = {
            "copied_from_url": seed_doc.get("copied_from_url"),
            "resourceType": seed_doc["resourceType"],
            "identifier": identifiers,
            "plan_groups": plan_groups,
            "is_seeded": False,
        }

        with open(new_path, "w", encoding="utf-8") as f:
            json.dump(new_doc, f, indent=2)
            f.write("\n")

        rel_new_path = os.path.relpath(new_path, REPO_ROOT).replace(os.sep, "/")
        stub_doc = {"is_seeded": False, "new_file": rel_new_path}
        with open(seed_path, "w", encoding="utf-8") as f:
            json.dump(stub_doc, f, indent=2)
            f.write("\n")

        n_plans = sum(len(pg["plan_identifiers"]) for pg in plan_groups)
        print(f"{entity_name}:")
        print(f"  seed -> {seed_path}  [replaced with stub]")
        print(f"  new  -> {new_path}")
        print(f"         ({len(identifiers)} identifiers, {len(plan_groups)} plan_group(s), "
              f"{n_plans} plan(s), FPI {new_fpi})")

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