#!/usr/bin/env python3
"""Run the lookup_url cleanup and the plan search-string derivation on the
four new Aetna Texas mockup well-known files.

This exists so the command line stays short:
    python tools/run_aetna_mockup_cleanup.py
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from remove_nonspecific_lookup_urls import LookupUrlCleaner  # noqa: E402
from plan_group_search_strings import PlanGroupSearchStrings  # noqa: E402

MEDICARE_ADVANTAGE_DIR = os.path.join(REPO_ROOT, "payer_index_files", "medicare_advantage")

NEW_AETNA_FILES = [
    os.path.join(
        MEDICARE_ADVANTAGE_DIR,
        "aetna_health_inc_tx",
        "aetna_health_inc_tx_b1affe56-4f6e-59a1-893e-f611f1dd8b5b.well_known_payer.json",
    ),
    os.path.join(
        MEDICARE_ADVANTAGE_DIR,
        "aetna_better_health_of_texas_inc",
        "aetna_better_health_of_texas_inc_3f9af4c3-d735-5c9b-9674-33cdd1864d6b.well_known_payer.json",
    ),
    os.path.join(
        MEDICARE_ADVANTAGE_DIR,
        "aetna_health_and_life_insurance_company",
        "aetna_health_and_life_insurance_company_68d4ceb9-93f6-548c-912b-f9f43eb79683.well_known_payer.json",
    ),
    os.path.join(
        MEDICARE_ADVANTAGE_DIR,
        "aetna_life_insurance_company",
        "aetna_life_insurance_company_a04283f0-5a1d-5df8-a744-e252652a1783.well_known_payer.json",
    ),
]

# NOTE: The filenames above reflect the FPIs produced by apply_aetna_texas_mockup.py
# using these approved source identifiers (per AI_Instructions/AetnaTexasMockup.md):
#   aetna_health_inc_tx            -> HIOS_ID  58840   -> b1affe56-4f6e-59a1-893e-f611f1dd8b5b
#   aetna_better_health_of_texas   -> STATE_DOI_ID TX-68775 -> 3f9af4c3-d735-5c9b-9674-33cdd1864d6b
#   aetna_health_and_life          -> NAIC_ID  78700   -> 68d4ceb9-93f6-548c-912b-f9f43eb79683
#   aetna_life_insurance_company   -> LEI SPCOIWBJM0HFYQX3A364 -> a04283f0-5a1d-5df8-a744-e252652a1783


def main():
    print("=== Step 1: remove non-specific lookup_urls ===")
    LookupUrlCleaner.run(file_paths=NEW_AETNA_FILES)
    print()
    print("=== Step 2: derive plan-level and plan-group search strings ===")
    PlanGroupSearchStrings.run(file_paths=NEW_AETNA_FILES)


if __name__ == "__main__":
    main()