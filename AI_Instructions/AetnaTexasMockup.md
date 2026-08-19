Ok.. so please read WellKnownFileFormat.md example_wellknown_payer_index.json GeneratingFederatedPayerIdentifiers.md and the ReadMe to understand how the well-known files are put together. Aetna has two texas entities. Aetna Health Inc. (Texas) and "Aetna Better Health of Texas, Inc." Some years ago, a company called "Texas Health" merged into Aetna Health Inc. (Texas) The well-known files that are being maintained are: 

* payer_index_files/medicare_advantage/aetna_better_health_of_texas_inc/aetna_better_health_of_texas_inc_e9a3ae68-5f89-594a-b281-6681770b34c2.well_known_payer.json 
* payer_index_files/medicare_advantage/aetna_health_inc_tx/aetna_health_inc_tx_6594b1a3-bfdb-5434-b228-
09d9cdfa8c87.well_known_payer.json 
* payer_index_files/medicare_advantage/aetna_health_and_life_insurance_company/aetna_health_and_life_insurance_company_4c7be225-8325-5765-b861-a9ebdf004a50.well_known_payer.json
* payer_index_files/medicare_advantage/aetna_life_insurance_company/aetna_life_insurance_company_565a5151-8480-5330-8910-4dfe0dab0717.well_known_payer.json

The payer identifiers that I have found for these two payers lives in mockup_data/aetna_texas_payer_identifiers.csv I want to modify the payer index files to reflect these new