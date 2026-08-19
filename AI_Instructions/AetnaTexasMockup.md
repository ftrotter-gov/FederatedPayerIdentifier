Aetna Mockup Instructions
=============

Ok.. so please read WellKnownFileFormat.md example_wellknown_payer_index.json GeneratingFederatedPayerIdentifiers.md and the ReadMe to understand how the well-known files are put together. Aetna has two texas entities. Aetna Health Inc. (Texas) and "Aetna Better Health of Texas, Inc." Some years ago, a company called "Texas Health" merged into Aetna Health Inc. (Texas) The well-known files that are being maintained are:

* payer_index_files/medicare_advantage/aetna_better_health_of_texas_inc/aetna_better_health_of_texas_inc_e9a3ae68-5f89-594a-b281-6681770b34c2.well_known_payer.json
* payer_index_files/medicare_advantage/aetna_health_inc_tx/aetna_health_inc_tx_6594b1a3-bfdb-5434-b228-
09d9cdfa8c87.well_known_payer.json
* payer_index_files/medicare_advantage/aetna_health_and_life_insurance_company/aetna_health_and_life_insurance_company_4c7be225-8325-5765-b861-a9ebdf004a50.well_known_payer.json
* payer_index_files/medicare_advantage/aetna_life_insurance_company/aetna_life_insurance_company_565a5151-8480-5330-8910-4dfe0dab0717.well_known_payer.json

The payer identifiers that I have found for these two payers lives in mockup_data/aetna_texas_payer_identifiers.csv I want to modify the payer index files to reflect these new
The rows labeled "Texas Health + Aetna Health Plan Inc." are all actually associated with the aetna_health_inc_tx entry as additional payer identifiers.

Modify the is_seeded for these records to equal "false" to start. This will prevent further overwritting.

I want to use these mockup to demonstrate the use of the FPI (i.e. different ways of choosing the generate the fpi uuid)

all of the other seeded values use the name hash as the source of the FPI.
But I want to use a different fpi source for each one (see ) specifically:

* NAIC_ID
* STATE_DOI_ID
* LEI
* HIOS_ID

Use tools/FPI_maker_cli.py to make the FPIs using these options. You may need to update the tool to reflect the updated versions of payer identifiction systems in reference_data/current_payer_identification_systems.json

We need to add "Aetna", to the list of payer_level_string_search_matches, as well as the company name without the word "Company" or "Inc." and the full legal company name"

Clarifying Questions and Answers
--------------

The following questions were asked and answered before development began:

1. **Which entity gets which FPI source?** It does not matter which entity gets which FPI source system, as long as each of the four entities uses a different one (NAIC_ID, STATE_DOI_ID, LEI, HIOS_ID). Note that the CSV data constrains this partially: only Aetna Health Inc. (TX) has a current HIOS_ID, and only Aetna Better Health of TX has the other current STATE_DOI_ID.

2. **File renames?** Yes, rename each well-known file so the filename contains the new FPI uuid. Leave the old file in place, containing nothing except `"is_seeded": false` and a new key called `"new_file"` that links to the new file (so that we can keep working with seed.py).

3. **Texas Health + Aetna Health Plan Inc. rows.** Ignore the CSV notes that say some rows merged into Aetna Life Insurance Company. Merge ALL "Texas Health + Aetna Health Plan Inc." rows into aetna_health_inc_tx as additional payer identifiers.

4. **Expired identifiers.** Yes, add the new metadata columns (e.g. expiration information from the CSV) to the identifier entries in the well-known files.

5. **Generic X12_PAYER_ID.** Add a generic `X12_PAYER_ID` system to reference_data/current_payer_identification_systems.json, and use it for the CSV's X12_PAYER_ID rows.

6. **EIN rows.** Do not use the EIN as an FPI source, but include the EINs in the "not-fpi" identifier list, just like all of the other payer identifiers.

7. **FPI_maker_cli.py update approach.** Modify the tool to load the payer identifier systems at runtime from reference_data/current_payer_identification_systems.json (instead of a hardcoded list).

8. **Keep the old legal_name_hash FPI?** No. Once we have a solid identifier we want to get rid of the hashes. Instead we should be relying on the payer search strings.

Second Round of Questions and Answers
--------------

9. **FPI source assignment (approved).** The following assignment was approved:

    | Entity | FPI source | Value |
    |---|---|---|
    | Aetna Health Inc. (TX) | HIOS_ID | 58840 |
    | Aetna Better Health of Texas, Inc. | STATE_DOI_ID | TX-68775 |
    | Aetna Health and Life Insurance Company | NAIC_ID | 78700 |
    | Aetna Life Insurance Company | LEI | SPCOIWBJM0HFYQX3A364 |

10. **STATE_DOI_ID collision prevention.** State DOI numbers are only unique within a state. Prefix state-level codes with the two-digit state code (e.g. `TX-68775`) to prevent collisions. Update the state-based uuid generation instructions and the source code in tools/FPI_maker_cli.py to do this. Also update GeneratingFederatedPayerIdentifiers.md to reflect this.

11. **Documentation updates.** GeneratingFederatedPayerIdentifiers.md also needs to be updated to note that the FPI itself is in the payer identifier system list (reference_data/current_payer_identification_systems.json). Also update the examples in example_wellknown_payer_index.json and WellKnownFileFormat.md to reflect the four-component first FPI entry in "identifier" (i.e. `system`, `value`, `fpi_source_system`, `fpi_source_value`).

12. **Generic X12_PAYER_ID reference entry wording.** No preferences on the description/assigning-authority wording.

13. **FPI_maker_cli menu scope.** Yes — exclude making FPIs from other FPIs (the `FPI` system itself must not be a selectable FPI source namespace in the CLI).
