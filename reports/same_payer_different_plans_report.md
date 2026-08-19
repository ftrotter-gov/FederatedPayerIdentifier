# Same Payer, Different Plans — Report

_Generated: 2026-08-19 02:39:05_

**Identity rule:** A payer is uniquely identified by its **Federated Payer Identifier (FPI)**. Directory names are for human convenience only. The intended design is **one file per payer**: plans with different endpoint sets are placed in separate `plan_groups` within that single file, and plans sharing the same endpoint set belong in the same `plan_group`. The same FPI appearing in multiple files is an anomaly worth review.

## Summary

| Metric | Count |
|--------|------:|
| Total payer files scanned | 142 |
| Files successfully parsed | 138 |
| Unique FPIs (distinct payers) | 138 |
| **FPIs appearing in multiple files** (anomalies to review) | **0** |
| FPIs appearing in exactly one file | 138 |
| Redirect/tombstone files (retired FPIs pointing to new files) | 4 |
| Files missing an FPI | 0 |
| Parse errors | 0 |

## Distribution: Number of Files per FPI (Payer)

Each row shows how many payers (FPIs) have exactly N files. Payers with N > 1 are anomalies: the intended design is one file per payer.

| Files per FPI | # Payers | Notes |
|-------------:|---------:|-------|
| 1 | 138 | expected: one file per payer |

## FPIs in Multiple Files (Anomalies to Review)

_No FPI currently appears in more than one file. This is the intended design: one file per payer, with distinct endpoint sets expressed as separate plan_groups within that file._

## Single-File Payers (Intended Design)

These **138 payers** each have exactly one file. Payers with more than one endpoint group are the 'same payer, different plans' cases, expressed as multiple plan_groups within their single file. Sorted by number of endpoint groups (descending), then plan count (descending).

| FPI | Payer Legal Name | # Endpoint Groups | # Plan IDs | Category |
|-----|-----------------|----------------:|----------:|----------|
| `635d88a7-4343-5d10-b6f9-19557bb2c090` | CALIFORNIA PHYSICIANS' SERVICE | 3 | [19](per_fpi/california_physicians_service.md) | medicare_advantage |
| `2bbe8987-ed5d-5d13-b000-f2bd8c58dcdd` | HEALTHFIRST HEALTH PLAN, INC. | 3 | [9](per_fpi/healthfirst_health_plan_inc.md) | medicare_advantage |
| `bab23acc-4386-5882-9251-499d422ab7eb` | DEVOTED HEALTH PLAN OF NORTH CAROLINA INC | 2 | [20](per_fpi/devoted_health_plan_of_north_carolina_inc.md) | medicare_advantage |
| `3caaab70-bd6b-5cea-9629-41464381631c` | DEVOTED HEALTH PLAN OF OHIO INC | 2 | [19](per_fpi/devoted_health_plan_of_ohio_inc.md) | medicare_advantage |
| `d476c29e-5c66-559b-99de-b11454be84bc` | HUMANA INSURANCE COMPANY | 1 | [330](per_fpi/humana_insurance_company.md) | medicare_advantage |
| `a04283f0-5a1d-5df8-a744-e252652a1783` | AETNA LIFE INSURANCE COMPANY | 1 | [237](per_fpi/aetna_life_insurance_company.md) | medicare_advantage |
| `4a1989ae-68b4-543d-8fd5-f1c450c570ee` | HEALTHSPRING LIFE & HEALTH INSURANCE COMPANY, INC. | 1 | [146](per_fpi/healthspring_life_health_insurance_company_inc.md) | medicare_advantage |
| `370fa3a4-f96c-597f-b3f8-926241f83db9` | EMPHESYS INSURANCE COMPANY | 1 | [115](per_fpi/emphesys_insurance_company.md) | medicare_advantage |
| `b8871bc5-892d-5703-be75-2d91a2b78e6f` | HUMANA MEDICAL PLAN, INC. | 1 | [108](per_fpi/humana_medical_plan_inc.md) | medicare_advantage |
| `be096f84-0f01-5721-acdb-c73ad89cf341` | ARCADIAN HEALTH PLAN, INC. | 1 | [74](per_fpi/arcadian_health_plan_inc.md) | medicare_advantage |
| `3a48f3e5-2910-567c-91d2-6c2e0ef84cc5` | DEVOTED HEALTH PLAN OF FLORIDA, INC. | 1 | [72](per_fpi/devoted_health_plan_of_florida_inc.md) | medicare_advantage |
| `4d80cbfa-cc05-5e98-85f8-4d9f86ace59f` | AETNA HEALTH INC. (PA) | 1 | [64](per_fpi/aetna_health_inc_pa.md) | medicare_advantage |
| `ff3610bd-c40f-5560-a648-96351050f884` | HUMANA WI HEALTH ORGANIZATION INSURANCE CORP | 1 | [59](per_fpi/humana_wi_health_organization_insurance_corp.md) | medicare_advantage |
| `1bb307a6-c023-59af-9a93-1b5ede7f0542` | HUMANA BENEFIT PLAN OF ILLINOIS, INC. | 1 | [55](per_fpi/humana_benefit_plan_of_illinois_inc.md) | medicare_advantage |
| `3a6fa3ac-04a2-5e6b-98ad-8849fc80d995` | AETNA HEALTH INC. (FL) | 1 | [51](per_fpi/aetna_health_inc_fl.md) | medicare_advantage |
| `5a9fa2fc-147e-57b9-8a9f-e43836218896` | CARITEN HEALTH PLAN INC. | 1 | [50](per_fpi/cariten_health_plan_inc.md) | medicare_advantage |
| `39e07b49-229e-5418-ba1b-098d94b8db21` | CHA HMO, INC. | 1 | [46](per_fpi/cha_hmo_inc.md) | medicare_advantage |
| `7bfc9422-b9e8-5393-a738-be518372b4af` | MMM HEALTHCARE, LLC | 1 | [44](per_fpi/mmm_healthcare_llc.md) | medicare_advantage |
| `d2688a5e-7e05-59a7-80d3-62c27e80162a` | COVENTRY HEALTH AND LIFE INSURANCE COMPANY | 1 | [38](per_fpi/coventry_health_and_life_insurance_company.md) | medicare_advantage |
| `2039ae24-53f2-58ec-8677-f7c958b2a2db` | CAREPLUS HEALTH PLANS, INC. | 1 | [33](per_fpi/careplus_health_plans_inc.md) | medicare_advantage |
| `690e8968-c344-5e46-84e7-0cb74305f4e1` | COVENTRY HEALTH CARE OF MISSOURI, INC. | 1 | [33](per_fpi/coventry_health_care_of_missouri_inc.md) | medicare_advantage |
| `3aa3a6db-78cd-50ce-a2a1-7607ecd6850c` | BRAVO HEALTH PENNSYLVANIA, INC. | 1 | [32](per_fpi/bravo_health_pennsylvania_inc.md) | medicare_advantage |
| `f1e4bbd8-5aa9-5dc3-b34c-ea6fb6e8bad3` | DEVOTED HEALTH PLAN OF TEXAS, INC. | 1 | [32](per_fpi/devoted_health_plan_of_texas_inc.md) | medicare_advantage |
| `3caf5cc9-552f-502f-bae2-0bbe8e520a69` | AETNA HEALTH OF OHIO INC. | 1 | [26](per_fpi/aetna_health_of_ohio_inc.md) | medicare_advantage |
| `68d4ceb9-93f6-548c-912b-f9f43eb79683` | AETNA HEALTH AND LIFE INSURANCE COMPANY | 1 | [25](per_fpi/aetna_health_and_life_insurance_company.md) | medicare_advantage |
| `d887d34b-5509-51a2-b57d-1ae20a8cb800` | FREEDOM HEALTH, INC. | 1 | [25](per_fpi/freedom_health_inc.md) | medicare_advantage |
| `970b75e4-7657-5182-b992-e3db65fd7431` | HUMANA HEALTH BENEFIT PLAN OF LOUISIANA, INC. | 1 | [24](per_fpi/humana_health_benefit_plan_of_louisiana_inc.md) | medicare_advantage |
| `b4b27b31-c5ef-5ecc-b231-0588abc286dc` | SOLIS HEALTH PLANS, INC. | 1 | [24](per_fpi/solis_health_plans_inc.md) | medicare_advantage |
| `0415a42d-47c6-55fa-91b8-c8faf3530002` | AETNA BETTER HEALTH INC. (GA) | 1 | [22](per_fpi/aetna_better_health_inc_ga.md) | medicare_advantage |
| `b1affe56-4f6e-59a1-893e-f611f1dd8b5b` | AETNA HEALTH INC. (TX) | 1 | [22](per_fpi/aetna_health_inc_tx.md) | medicare_advantage |
| `1a33c798-a7df-56d7-a4c4-b1e6ee93e751` | DEVOTED HEALTH PLAN OF PENNSYLVANIA INC | 1 | [20](per_fpi/devoted_health_plan_of_pennsylvania_inc.md) | medicare_advantage |
| `254facaa-4ace-5db7-af42-85e91921c307` | AETNA HEALTH INC. (NY) | 1 | [19](per_fpi/aetna_health_inc_ny.md) | medicare_advantage |
| `e9895113-428b-54c4-9c55-f6593b0c8e0f` | HUMANA INSURANCE COMPANY OF NEW YORK | 1 | [19](per_fpi/humana_insurance_company_of_new_york.md) | medicare_advantage |
| `e4727998-af85-5e5f-81a9-0947f9bf23bb` | COVENTRY HEALTH CARE OF ILLINOIS, INC. | 1 | [18](per_fpi/coventry_health_care_of_illinois_inc.md) | medicare_advantage |
| `44d60086-fc07-5d51-a36e-16aee6a23975` | HEALTHSPRING OF FLORIDA, INC. | 1 | [17](per_fpi/healthspring_of_florida_inc.md) | medicare_advantage |
| `d762c1aa-f916-53c2-95c4-d4be587289cb` | SILVERSCRIPT INSURANCE COMPANY | 1 | [17](per_fpi/silverscript_insurance_company.md) | medicare_advantage |
| `3f2c6711-c405-5110-84e6-b322cdbe97a0` | AETNA BETTER HEALTH, INC. (LA) | 1 | [16](per_fpi/aetna_better_health_inc_la.md) | medicare_advantage |
| `2fa615f5-20ec-5683-8cf2-a18805b5160b` | DEVOTED HEALTH PLAN OF MISSOURI INC | 1 | [16](per_fpi/devoted_health_plan_of_missouri_inc.md) | medicare_advantage |
| `6c19728c-663a-5670-be98-9159991269c1` | AETNA HEALTH OF CALIFORNIA INC. | 1 | [15](per_fpi/aetna_health_of_california_inc.md) | medicare_advantage |
| `78d74282-7f45-56b1-aca4-4a677226d554` | DEVOTED HEALTH INSURANCE COMPANY OF INDIANA | 1 | [15](per_fpi/devoted_health_insurance_company_of_indiana.md) | medicare_advantage |
| `3bb55a39-a5c1-5e2b-9cd0-cc550ecebd15` | DEVOTED HEALTH PLAN OF ARIZONA, INC. | 1 | [15](per_fpi/devoted_health_plan_of_arizona_inc.md) | medicare_advantage |
| `46e73cb0-a030-514a-a368-3bd63e32a5f7` | OPTIMUM HEALTHCARE, INC. | 1 | [15](per_fpi/optimum_healthcare_inc.md) | medicare_advantage |
| `4afe6536-df1c-526e-ab3d-3078535a4917` | DEVOTED HEALTH INSURANCE COMPANY OF ALABAMA INC | 1 | [13](per_fpi/devoted_health_insurance_company_of_alabama_inc.md) | medicare_advantage |
| `c2423511-7df0-52e2-b976-d5f68d1a734c` | DEVOTED HEALTH INSURANCE COMPANY OF TENNESSEE INC | 1 | [13](per_fpi/devoted_health_insurance_company_of_tennessee_inc.md) | medicare_advantage |
| `247afaad-1689-5305-8225-3cffeca4cb6e` | HEALTHSUN HEALTH PLANS, INC. | 1 | [13](per_fpi/healthsun_health_plans_inc.md) | medicare_advantage |
| `6efca3f5-3a86-5dce-8fc0-20fac4e81158` | AETNA HEALTH OF MICHIGAN INC. | 1 | [12](per_fpi/aetna_health_of_michigan_inc.md) | medicare_advantage |
| `6ec2d199-297f-5dd2-aec2-0a753eb8bbc7` | BLUE CROSS AND BLUE SHIELD OF ALABAMA | 1 | [12](per_fpi/blue_cross_and_blue_shield_of_alabama.md) | medicare_advantage |
| `0286aa80-272b-576c-a884-9e323eabc016` | ALLINA HEALTH AND AETNA INSURANCE COMPANY | 1 | [11](per_fpi/allina_health_and_aetna_insurance_company.md) | medicare_advantage |
| `5e3e074f-543d-55b9-981c-e1b90788830d` | DEVOTED HEALTH INSURANCE COMPANY OF GEORGIA INC | 1 | [11](per_fpi/devoted_health_insurance_company_of_georgia_inc.md) | medicare_advantage |
| `e7b17873-5b98-5ded-b1fd-7e8514371b94` | HEALTH FIRST HEALTH PLANS | 1 | [11](per_fpi/health_first_health_plans.md) | medicare_advantage |
| `0606f1aa-ca84-5a54-bf1b-e9d5c08dca9a` | HEALTHSPRING HEALTHCARE OF COLORADO, INC. | 1 | [11](per_fpi/healthspring_healthcare_of_colorado_inc.md) | medicare_advantage |
| `73f59c79-a1a6-5339-9720-e0c4981b0884` | HUMANA EMPLOYERS HEALTH PLAN OF GEORGIA, INC. | 1 | [11](per_fpi/humana_employers_health_plan_of_georgia_inc.md) | medicare_advantage |
| `11bc9f14-6b58-5f56-9f65-fd80c8b21d92` | AETNA BETTER HEALTH OF CALIFORNIA INC. | 1 | [10](per_fpi/aetna_better_health_of_california_inc.md) | medicare_advantage |
| `98db7c7a-69f6-5afa-bc4a-300ff25d0901` | AETNA HEALTH INC. (CT) | 1 | [10](per_fpi/aetna_health_inc_ct.md) | medicare_advantage |
| `7e79a360-e83c-516e-9b4c-7868d98042fa` | AETNA HEALTH INC. (GA) | 1 | [10](per_fpi/aetna_health_inc_ga.md) | medicare_advantage |
| `ce7fd07d-860a-55bb-b34c-d528c80e6707` | AULTCARE HEALTH INSURING CORPORATION | 1 | [10](per_fpi/aultcare_health_insuring_corporation.md) | medicare_advantage |
| `ea4455af-35df-5c1d-aeb5-7fda4f188fa2` | COVENTRY HEALTH CARE OF KANSAS, INC. | 1 | [10](per_fpi/coventry_health_care_of_kansas_inc.md) | medicare_advantage |
| `dc49966c-ef33-5a5a-9faa-c938be4c3238` | DEVOTED HEALTH PLAN OF VIRGINIA INC | 1 | [10](per_fpi/devoted_health_plan_of_virginia_inc.md) | medicare_advantage |
| `03b95fb8-1315-5f8c-a475-113b0875fd27` | Devoted of Illinois, Inc. | 1 | [10](per_fpi/devoted_of_illinois_inc.md) | medicare_advantage |
| `9b799d4a-869b-5fa5-b42f-2ff73a7b36ca` | HUMANA MEDICAL PLAN OF MICHIGAN, INC. | 1 | [10](per_fpi/humana_medical_plan_of_michigan_inc.md) | medicare_advantage |
| `398330a4-57c3-5fac-a74a-e543db856de2` | BRAVO HEALTH MID-ATLANTIC, INC. | 1 | [9](per_fpi/bravo_health_mid_atlantic_inc.md) | medicare_advantage |
| `403ccf65-b4d8-57fe-9d12-ffdb2f7cf518` | COVENTRY HEALTH CARE OF NEBRASKA, INC. | 1 | [9](per_fpi/coventry_health_care_of_nebraska_inc.md) | medicare_advantage |
| `acd45b79-a4a6-5687-a462-d248686829f4` | DEVOTED HEALTH INSURANCE COMPANY OF LOUISIANA | 1 | [9](per_fpi/devoted_health_insurance_company_of_louisiana.md) | medicare_advantage |
| `626f8c14-47a2-591b-961d-de51a0256ac9` | DEVOTED HEALTH PLAN OF COLORADO INC | 1 | [9](per_fpi/devoted_health_plan_of_colorado_inc.md) | medicare_advantage |
| `fbec3978-71ec-59a3-9d22-e284132f39af` | DEVOTED HEALTH PLAN OF TENNESSEE INC | 1 | [9](per_fpi/devoted_health_plan_of_tennessee_inc.md) | medicare_advantage |
| `5233cc6f-4f6c-51c0-9481-e62ddee6d401` | DOCTORS HEALTHCARE PLANS, INC. | 1 | [9](per_fpi/doctors_healthcare_plans_inc.md) | medicare_advantage |
| `d16a22b6-80af-508f-9da5-9037a30e3b42` | HUMANA HEALTH COMPANY OF NEW YORK, INC. | 1 | [9](per_fpi/humana_health_company_of_new_york_inc.md) | medicare_advantage |
| `44681ced-513f-5281-9d49-b06e6b34a068` | AETNA HEALTH INC. (NJ) | 1 | [8](per_fpi/aetna_health_inc_nj.md) | medicare_advantage |
| `d1dcfe38-272a-5b66-86b2-057c1db30f6c` | BLUE CROSS & BLUE SHIELD OF RHODE ISLAND | 1 | [8](per_fpi/blue_cross_blue_shield_of_rhode_island.md) | medicare_advantage |
| `49983cba-58ba-5818-84c8-a627900d48f0` | DEVOTED HEALTH INSURANCE COMPANY OF ARKANSAS INC | 1 | [8](per_fpi/devoted_health_insurance_company_of_arkansas_inc.md) | medicare_advantage |
| `da1e0b80-94de-58fb-8df2-0ef0c3576281` | DEVOTED HEALTH INSURANCE COMPANY OF MISSISSIPPI | 1 | [8](per_fpi/devoted_health_insurance_company_of_mississippi.md) | medicare_advantage |
| `68f5c7e3-c22e-566f-8211-04f2a0cdee59` | DEVOTED HEALTH INSURANCE COMPANY OF OKLAHOMA | 1 | [8](per_fpi/devoted_health_insurance_company_of_oklahoma.md) | medicare_advantage |
| `0c757d3c-3f79-5038-80b6-179409756b1d` | AETNA HEALTH INC. (ME) | 1 | [7](per_fpi/aetna_health_inc_me.md) | medicare_advantage |
| `cd908614-d9bf-5228-aa04-b6da9917f936` | DEVOTED HEALTH INSURANCE COMPANY OF HAWAII INC | 1 | [7](per_fpi/devoted_health_insurance_company_of_hawaii_inc.md) | medicare_advantage |
| `3df92505-613b-554c-bc5b-5625cfd2cc56` | DEVOTED HEALTH INSURANCE COMPANY OF KANSAS | 1 | [7](per_fpi/devoted_health_insurance_company_of_kansas.md) | medicare_advantage |
| `e4618178-3ebe-5b71-8b8f-ba91060cf9c6` | DEVOTED HEALTH PLAN OF NEW MEXICO, INC. | 1 | [7](per_fpi/devoted_health_plan_of_new_mexico_inc.md) | medicare_advantage |
| `6eb4e6e5-0cb0-5be8-9c63-009824d8abea` | HUMANA MEDICAL PLAN OF UTAH, INC. | 1 | [7](per_fpi/humana_medical_plan_of_utah_inc.md) | medicare_advantage |
| `4e50d9b5-b289-5ca9-8560-d62a1dc8c1e3` | COVENTRY HEALTH CARE OF WEST VIRGINIA, INC. | 1 | [6](per_fpi/coventry_health_care_of_west_virginia_inc.md) | medicare_advantage |
| `9fb82109-bf6e-5a6d-af57-6ba1435e7b85` | DEVOTED HEALTH INSURANCE COMPANY OF KENTUCKY INC | 1 | [6](per_fpi/devoted_health_insurance_company_of_kentucky_inc.md) | medicare_advantage |
| `a66fa3e7-48b4-5849-9283-e2409f3ad9b6` | DEVOTED HEALTH INSURANCE COMPANY OF NEBRASKA | 1 | [6](per_fpi/devoted_health_insurance_company_of_nebraska.md) | medicare_advantage |
| `aed49611-dc38-5a87-938a-afbea0f1a57e` | DEVOTED HEALTH INSURANCE COMPANY OF PENNSYLVANIA INC | 1 | [6](per_fpi/devoted_health_insurance_company_of_pennsylvania_inc.md) | medicare_advantage |
| `57ea794b-dd03-55ee-9bb5-b275b25034e4` | DEVOTED HEALTH INSURANCE COMPANY OF SOUTH CAROLINA INC | 1 | [6](per_fpi/devoted_health_insurance_company_of_south_carolina_inc.md) | medicare_advantage |
| `4810a8d7-7c44-5f44-8d81-5b72e3e5cb0f` | DEVOTED HEALTH PLAN OF ALABAMA INC | 1 | [6](per_fpi/devoted_health_plan_of_alabama_inc.md) | medicare_advantage |
| `19709589-580f-56c1-9b90-037c19739bf3` | DEVOTED HEALTH PLAN OF OREGON INC | 1 | [6](per_fpi/devoted_health_plan_of_oregon_inc.md) | medicare_advantage |
| `bb51ea7b-fd3f-5ff5-beea-b98af7e62fde` | AETNA BETTER HEALTH OF MICHIGAN INC. | 1 | [5](per_fpi/aetna_better_health_of_michigan_inc.md) | medicare_advantage |
| `74fd82a4-e0f7-588e-8fde-a1bf63d4fb5c` | DEVOTED HEALTH INSURANCE COMPANY OF ARIZONA, INC. | 1 | [5](per_fpi/devoted_health_insurance_company_of_arizona_inc.md) | medicare_advantage |
| `3671e72a-6ebe-5f33-af79-f1c822f2c0e2` | DEVOTED HEALTH INSURANCE COMPANY OF COLORADO INC | 1 | [5](per_fpi/devoted_health_insurance_company_of_colorado_inc.md) | medicare_advantage |
| `3e758bc9-6dec-5be8-b4a1-7147b5ebab41` | DEVOTED HEALTH INSURANCE COMPANY OF UTAH, INC. | 1 | [5](per_fpi/devoted_health_insurance_company_of_utah_inc.md) | medicare_advantage |
| `f612e97f-3660-57b3-8374-f6f1ab719b72` | DEVOTED HEALTH PLAN OF HAWAII, INC. | 1 | [5](per_fpi/devoted_health_plan_of_hawaii_inc.md) | medicare_advantage |
| `29975961-9181-5919-91c9-35455cfca15e` | AETNA HEALTH OF UTAH INC. | 1 | [4](per_fpi/aetna_health_of_utah_inc.md) | medicare_advantage |
| `a504acc0-8289-56b3-bd5f-2609df7b3c62` | DEVOTED HEALTH INSURANCE COMPANY | 1 | [4](per_fpi/devoted_health_insurance_company.md) | medicare_advantage |
| `7486d04b-a322-51d7-a00f-949f823d3cd6` | DEVOTED HEALTH INSURANCE COMPANY OF WASHINGTON | 1 | [4](per_fpi/devoted_health_insurance_company_of_washington.md) | medicare_advantage |
| `ce05d53c-c22d-57fa-be66-1a06fc759846` | DEVOTED HEALTH PLAN OF ILLINOIS, INC. | 1 | [4](per_fpi/devoted_health_plan_of_illinois_inc.md) | medicare_advantage |
| `dddfbbf5-7b02-5206-80df-79b7bbb0efa9` | HUMANA HEALTH INSURANCE COMPANY OF FLORIDA, INC. | 1 | [4](per_fpi/humana_health_insurance_company_of_florida_inc.md) | medicare_advantage |
| `7c455315-7920-5f4f-8bc6-e9a81336da1c` | LEON HEALTH, INC. | 1 | [4](per_fpi/leon_health_inc.md) | medicare_advantage |
| `5b1f62f0-889c-50d6-872a-73607a4f8fec` | MEDISUN, INC. | 1 | [4](per_fpi/medisun_inc.md) | medicare_advantage |
| `d6799be6-ce1d-58d0-b114-8d4711e7d92d` | AETNA BETTER HEALTH OF OKLAHOMA INC. | 1 | [3](per_fpi/aetna_better_health_of_oklahoma_inc.md) | medicare_advantage |
| `3f9af4c3-d735-5c9b-9674-33cdd1864d6b` | AETNA BETTER HEALTH OF TEXAS INC. | 1 | [3](per_fpi/aetna_better_health_of_texas_inc.md) | medicare_advantage |
| `ae111e98-25f2-5085-b19c-1320fe0a76e0` | AETNA HEALTH INC. (LA) | 1 | [3](per_fpi/aetna_health_inc_la.md) | medicare_advantage |
| `80b2acbb-a674-5a5d-97fd-e4006d9d2bd9` | DEVOTED HEALTH INSURANCE COMPANY OF DELAWARE | 1 | [3](per_fpi/devoted_health_insurance_company_of_delaware.md) | medicare_advantage |
| `21840c71-6646-5780-b2ee-2b62d7921268` | HUMANA HEALTH PLAN OF OHIO, INC. | 1 | [3](per_fpi/humana_health_plan_of_ohio_inc.md) | medicare_advantage |
| `f8a84207-4ba2-58f6-9b36-755af38fa100` | HUMANA INSURANCE COMPANY OF KENTUCKY | 1 | [3](per_fpi/humana_insurance_company_of_kentucky.md) | medicare_advantage |
| `4b0b6575-0260-5362-8c45-0c04dc067752` | VILLAGE SENIOR SERVICES CORPORATION | 1 | [3](per_fpi/village_senior_services_corporation.md) | medicare_advantage |
| `4321b5af-766f-54ac-9fd5-90e4e2377af4` | AETNA BETTER HEALTH OF WASHINGTON, INC. | 1 | [2](per_fpi/aetna_better_health_of_washington_inc.md) | medicare_advantage |
| `5fca82db-3e97-5415-a9fa-4bf66d449cda` | AETNA HEALTH OF IOWA INC. | 1 | [2](per_fpi/aetna_health_of_iowa_inc.md) | medicare_advantage |
| `6e67dd5d-47ea-521a-ac0c-4a53e18a83ea` | AMERICAN HEALTH PLAN OF IOWA INC | 1 | [2](per_fpi/american_health_plan_of_iowa_inc.md) | medicare_advantage |
| `9fa27371-8c30-5ade-951c-2dd21361dfc0` | AMERICAN HEALTH PLAN OF MISSOURI, INC. | 1 | [2](per_fpi/american_health_plan_of_missouri_inc.md) | medicare_advantage |
| `431b920f-2235-548c-be6e-9f931d95e051` | AMERICAN HEALTH PLAN OF UT, INC. | 1 | [2](per_fpi/american_health_plan_of_ut_inc.md) | medicare_advantage |
| `de99dd67-a726-5a76-afa4-6c981c1ebdb8` | DEVOTED HEALTH INSURANCE COMPANY OF TEXAS | 1 | [2](per_fpi/devoted_health_insurance_company_of_texas.md) | medicare_advantage |
| `2f35b9ac-6e7f-5a2c-a719-df7818400793` | DEVOTED HEALTH PLAN OF SOUTH CAROLINA INC | 1 | [2](per_fpi/devoted_health_plan_of_south_carolina_inc.md) | medicare_advantage |
| `8cdb091d-1745-5bfd-a2a0-1e5c06ff79a5` | Devoted Health Insurance Company of Illinois, Inc. | 1 | [2](per_fpi/devoted_health_insurance_company_of_illinois_inc.md) | medicare_advantage |
| `0b4c9d01-a10c-50fa-9f17-eff87f42dfe9` | FIRST HEALTH LIFE & HEALTH INSURANCE COMPANY | 1 | [2](per_fpi/first_health_life_health_insurance_company.md) | medicare_advantage |
| `2c232d65-57df-5067-9dbb-29e1348f520b` | GEORGIA ASSURANCE, INC. | 1 | [2](per_fpi/georgia_assurance_inc.md) | medicare_advantage |
| `f757db87-c3aa-50d3-9af8-65408fc6c6ce` | HUMANA MEDICAL PLAN OF PENNSYLVANIA, INC. | 1 | [2](per_fpi/humana_medical_plan_of_pennsylvania_inc.md) | medicare_advantage |
| `2fd928a9-9d9a-52d4-83ce-692b6ac8dd1c` | HUMANA REGIONAL HEALTH PLAN, INC. | 1 | [2](per_fpi/humana_regional_health_plan_inc.md) | medicare_advantage |
| `59aafe7b-7114-5c6f-8dac-a86e2ca4c7be` | KANSAS SUPERIOR SELECT, INC. | 1 | [2](per_fpi/kansas_superior_select_inc.md) | medicare_advantage |
| `487bc10e-ff98-5890-8e7c-9bb0a0da2c0c` | TEXAS INDEPENDENCE HEALTH PLAN, INC. | 1 | [2](per_fpi/texas_independence_health_plan_inc.md) | medicare_advantage |
| `a85212d5-c543-5afb-a036-e1f3379adf23` | AETNA BETTER HEALTH INC. (NJ) | 1 | [1](per_fpi/aetna_better_health_inc_nj.md) | medicare_advantage |
| `59915f0c-a88e-5fc1-b5b5-c9688f902660` | AETNA BETTER HEALTH PREMIER PLAN MMAI INC. | 1 | [1](per_fpi/aetna_better_health_premier_plan_mmai_inc.md) | medicare_advantage |
| `19b9ee07-50ea-5182-80cb-a5167b1e9592` | AMERICAN HEALTH PLAN OF FL, INC. | 1 | [1](per_fpi/american_health_plan_of_fl_inc.md) | medicare_advantage |
| `036a8cf6-29fc-51c7-beec-d40d3224688b` | AMERICAN HEALTH PLAN OF INDIANA INC | 1 | [1](per_fpi/american_health_plan_of_indiana_inc.md) | medicare_advantage |
| `db183419-12c5-50d8-bb54-b5fd2d416846` | AMERICAN HEALTH PLAN OF MS, INC. | 1 | [1](per_fpi/american_health_plan_of_ms_inc.md) | medicare_advantage |
| `147cd3e4-7ce2-518f-af95-9b178048a1a3` | AMERICAN HEALTH PLAN OF PENNSYLVANIA INC | 1 | [1](per_fpi/american_health_plan_of_pennsylvania_inc.md) | medicare_advantage |
| `1abb9417-7a53-514b-9514-e694db6de753` | AMERICAN HEALTH PLAN OF TX, INC. | 1 | [1](per_fpi/american_health_plan_of_tx_inc.md) | medicare_advantage |
| `b7de864c-bbc4-5c7b-9c46-1deef0f3bc29` | AMERICAN HEALTH PLAN, INC. | 1 | [1](per_fpi/american_health_plan_inc.md) | medicare_advantage |
| `daad03cc-f8c6-52d4-8b26-456170a58607` | CONTRA COSTA COUNTY MEDICAL SERVICE DBA CONTRA COSTA HEALTH PLAN | 1 | [1](per_fpi/contra_costa_county_medical_service_dba_contra_costa_health_plan.md) | medicare_advantage |
| `f9b4c561-14af-50e1-a571-cba36f6daab0` | COVENTRY HEALTH CARE OF VIRGINIA, INC. | 1 | [1](per_fpi/coventry_health_care_of_virginia_inc.md) | medicare_advantage |
| `a361bf4a-9fb0-5eaa-afc2-70ae4c8ac118` | DEVOTED HEALTH  PLAN OF OREGON | 1 | [1](per_fpi/devoted_health_plan_of_oregon.md) | medicare_advantage |
| `f7ab7fb8-7eb6-55ae-8bfd-b1cce1519e75` | DIGNITY CARE CORPORATION | 1 | [1](per_fpi/dignity_care_corporation.md) | medicare_advantage |
| `d9a598f3-208c-5795-a616-3569f2363ca1` | HEALTHFIRST INSURANCE COMPANY, INC. | 1 | [1](per_fpi/healthfirst_insurance_company_inc.md) | medicare_advantage |
| `387dce3d-56cc-58af-bc38-b60e42c5ceba` | HUMANA BENEFIT PLAN OF SOUTH CAROLINA, INC. | 1 | [1](per_fpi/humana_benefit_plan_of_south_carolina_inc.md) | medicare_advantage |
| `826c7416-72f5-5bf7-88af-c2bc08d42e79` | HUMANA HEALTH PLAN OF TEXAS, INC. | 1 | [1](per_fpi/humana_health_plan_of_texas_inc.md) | medicare_advantage |
| `0ed84fb5-7e56-5fa8-89cf-161369bb50d5` | HUMANA HEALTH PLAN, INC. | 1 | [1](per_fpi/humana_health_plan_inc.md) | medicare_advantage |
| `9f810bfc-2cd8-5a4f-a7e2-8cface212c5e` | INDEPENDENT CARE HEALTH PLAN | 1 | [1](per_fpi/independent_care_health_plan.md) | medicare_advantage |
| `a3862519-16ae-566b-98c8-c6cf5c46c92b` | Inland Empire Health Plan | 1 | [1](per_fpi/inland_empire_health_plan.md) | medicare_advantage |
| `a641782e-f45f-576a-b772-d8ac01c18216` | LOCAL INITIATIVE HEALTH AUTHORITY FOR LA COUNTY | 1 | [1](per_fpi/local_initiative_health_authority_for_la_county.md) | medicare_advantage |
| `64f76a87-585c-5c93-af0f-ec64d53cc950` | OKLAHOMA SUPERIOR SELECT, INC. | 1 | [1](per_fpi/oklahoma_superior_select_inc.md) | medicare_advantage |
| `ce532baa-daae-56cd-a0a1-1b034130c3a4` | SANTA CLARA COUNTY HEALTH AUTHORITY | 1 | [1](per_fpi/santa_clara_county_health_authority.md) | medicare_advantage |

## Redirect / Tombstone Files

These files carry a retired FPI in their filename and contain only a `new_file` pointer to the payer's current well-known file:

- `medicare_advantage/aetna_better_health_of_texas_inc/aetna_better_health_of_texas_inc_e9a3ae68-5f89-594a-b281-6681770b34c2.well_known_payer.json` → `payer_index_files/medicare_advantage/aetna_better_health_of_texas_inc/aetna_better_health_of_texas_inc_3f9af4c3-d735-5c9b-9674-33cdd1864d6b.well_known_payer.json`
- `medicare_advantage/aetna_health_and_life_insurance_company/aetna_health_and_life_insurance_company_4c7be225-8325-5765-b861-a9ebdf004a50.well_known_payer.json` → `payer_index_files/medicare_advantage/aetna_health_and_life_insurance_company/aetna_health_and_life_insurance_company_68d4ceb9-93f6-548c-912b-f9f43eb79683.well_known_payer.json`
- `medicare_advantage/aetna_health_inc_tx/aetna_health_inc_tx_6594b1a3-bfdb-5434-b228-09d9cdfa8c87.well_known_payer.json` → `payer_index_files/medicare_advantage/aetna_health_inc_tx/aetna_health_inc_tx_b1affe56-4f6e-59a1-893e-f611f1dd8b5b.well_known_payer.json`
- `medicare_advantage/aetna_life_insurance_company/aetna_life_insurance_company_565a5151-8480-5330-8910-4dfe0dab0717.well_known_payer.json` → `payer_index_files/medicare_advantage/aetna_life_insurance_company/aetna_life_insurance_company_a04283f0-5a1d-5df8-a744-e252652a1783.well_known_payer.json`

