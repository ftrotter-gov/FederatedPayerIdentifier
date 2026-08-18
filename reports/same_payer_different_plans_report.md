# Same Payer, Different Plans — Report

_Generated: 2026-08-18 19:10:24_

**Identity rule:** A payer is uniquely identified by its **Federated Payer Identifier (FPI)**. Directory names are for human convenience only. The same FPI appearing in **multiple files** is the intended design when a payer has plans with different endpoint sets — each file covers one distinct endpoint configuration. Plans sharing the same endpoint set belong in the same `plan_group` within a single file.

## Summary

| Metric | Count |
|--------|------:|
| Total payer files scanned | 138 |
| Files successfully parsed | 138 |
| Unique FPIs (distinct payers) | 138 |
| **FPIs appearing in multiple files** (same payer, different endpoint sets) | **0** |
| FPIs appearing in exactly one file | 138 |
| Files missing an FPI | 0 |
| Parse errors | 0 |

## Distribution: Number of Files per FPI (Payer)

Each row shows how many payers (FPIs) have exactly N files. Payers with N > 1 are the 'same payer, different plans' cases.

| Files per FPI | # Payers | Notes |
|-------------:|---------:|-------|
| 1 | 138 | all plans share the same endpoint set |

## Same Payer, Different Plans (FPIs in Multiple Files)

_No FPI currently appears in more than one file. This means every payer's plans currently share identical endpoint sets (all plans are in a single file per payer). This is valid — it simply means no payer yet has plans requiring distinct endpoint configurations._

## Single-File Payers (All Plans Share One Endpoint Set)

These **138 payers** each have exactly one file. Sorted by number of endpoint groups (descending), then plan count (descending).

| FPI | Payer Legal Name | # Endpoint Groups | # Plan IDs | Category |
|-----|-----------------|----------------:|----------:|----------|
| `533e8cda-e553-5215-a289-6eb5d030bda4` | CALIFORNIA PHYSICIANS' SERVICE | 3 | [19](per_fpi/california_physicians_service.md) | medicare_advantage |
| `01686f3a-6420-5c50-8bb6-cdac50dd3309` | HEALTHFIRST HEALTH PLAN, INC. | 3 | [9](per_fpi/healthfirst_health_plan_inc.md) | medicare_advantage |
| `0cff5ca8-dafa-5ab3-88d6-3ac2d4c428ab` | DEVOTED HEALTH PLAN OF NORTH CAROLINA INC | 2 | [20](per_fpi/devoted_health_plan_of_north_carolina_inc.md) | medicare_advantage |
| `219fe8f3-6352-57ae-a44e-5f86bc28b1ad` | DEVOTED HEALTH PLAN OF OHIO INC | 2 | [19](per_fpi/devoted_health_plan_of_ohio_inc.md) | medicare_advantage |
| `596491f0-3125-5a7b-b1a3-f4d99a22b8d8` | HUMANA INSURANCE COMPANY | 1 | [320](per_fpi/humana_insurance_company.md) | medicare_advantage |
| `565a5151-8480-5330-8910-4dfe0dab0717` | AETNA LIFE INSURANCE COMPANY | 1 | [237](per_fpi/aetna_life_insurance_company.md) | medicare_advantage |
| `7693f86c-8fb0-5e2c-a279-978e6627bf62` | HEALTHSPRING LIFE & HEALTH INSURANCE COMPANY, INC. | 1 | [143](per_fpi/healthspring_life_health_insurance_company_inc.md) | medicare_advantage |
| `05981a59-0694-5d91-bfbb-84b553318325` | EMPHESYS INSURANCE COMPANY | 1 | [115](per_fpi/emphesys_insurance_company.md) | medicare_advantage |
| `0f014f79-57f9-5bde-81b2-ad0903a8a860` | HUMANA MEDICAL PLAN, INC. | 1 | [108](per_fpi/humana_medical_plan_inc.md) | medicare_advantage |
| `7dc2d2ac-6d83-51c9-9bf8-fd4639834dd2` | ARCADIAN HEALTH PLAN, INC. | 1 | [74](per_fpi/arcadian_health_plan_inc.md) | medicare_advantage |
| `df52c8f8-8df4-5cef-974a-b6d77cd869be` | DEVOTED HEALTH PLAN OF FLORIDA, INC. | 1 | [72](per_fpi/devoted_health_plan_of_florida_inc.md) | medicare_advantage |
| `0f088bd6-956e-5707-98d6-8c9d95e94660` | AETNA HEALTH INC. (PA) | 1 | [62](per_fpi/aetna_health_inc_pa.md) | medicare_advantage |
| `4b7ade48-0f81-5ebd-a8d7-15fd52d64797` | HUMANA WI HEALTH ORGANIZATION INSURANCE CORP | 1 | [59](per_fpi/humana_wi_health_organization_insurance_corp.md) | medicare_advantage |
| `0f9ae154-d440-5da5-b03b-5a0ff3d35680` | HUMANA BENEFIT PLAN OF ILLINOIS, INC. | 1 | [55](per_fpi/humana_benefit_plan_of_illinois_inc.md) | medicare_advantage |
| `24f1fcc8-af35-59ea-9aa4-b71b3a515d3e` | AETNA HEALTH INC. (FL) | 1 | [51](per_fpi/aetna_health_inc_fl.md) | medicare_advantage |
| `42c263fa-83c7-50c4-ae68-e455ef758645` | CARITEN HEALTH PLAN INC. | 1 | [50](per_fpi/cariten_health_plan_inc.md) | medicare_advantage |
| `890a9a8e-8446-5fb5-9043-798abf8e52f6` | CHA HMO, INC. | 1 | [46](per_fpi/cha_hmo_inc.md) | medicare_advantage |
| `76d54476-682c-5072-a7e6-3910b5de8723` | MMM HEALTHCARE, LLC | 1 | [44](per_fpi/mmm_healthcare_llc.md) | medicare_advantage |
| `70a03b45-4b59-5a7b-9362-1473b6e72b68` | COVENTRY HEALTH AND LIFE INSURANCE COMPANY | 1 | [38](per_fpi/coventry_health_and_life_insurance_company.md) | medicare_advantage |
| `9cbc9a86-ff7e-5371-aa71-699acf45e4b4` | CAREPLUS HEALTH PLANS, INC. | 1 | [33](per_fpi/careplus_health_plans_inc.md) | medicare_advantage |
| `adb16788-0755-553f-aa14-127810128324` | COVENTRY HEALTH CARE OF MISSOURI, INC. | 1 | [33](per_fpi/coventry_health_care_of_missouri_inc.md) | medicare_advantage |
| `0f6fa9c2-5dc9-5f3a-afe6-ed3fb3a2f1d8` | DEVOTED HEALTH PLAN OF TEXAS, INC. | 1 | [32](per_fpi/devoted_health_plan_of_texas_inc.md) | medicare_advantage |
| `a9b78a98-f221-5292-b524-182511ac850d` | BRAVO HEALTH PENNSYLVANIA, INC. | 1 | [31](per_fpi/bravo_health_pennsylvania_inc.md) | medicare_advantage |
| `dec23187-3614-53c7-8640-ce8c2f64f701` | AETNA HEALTH OF OHIO INC. | 1 | [26](per_fpi/aetna_health_of_ohio_inc.md) | medicare_advantage |
| `4c7be225-8325-5765-b861-a9ebdf004a50` | AETNA HEALTH AND LIFE INSURANCE COMPANY | 1 | [25](per_fpi/aetna_health_and_life_insurance_company.md) | medicare_advantage |
| `a7a8a0de-4df9-5bd2-bffd-d90925f4024a` | FREEDOM HEALTH, INC. | 1 | [25](per_fpi/freedom_health_inc.md) | medicare_advantage |
| `2aaf1a66-68a1-5846-be5f-fd5105cdf184` | HUMANA HEALTH BENEFIT PLAN OF LOUISIANA, INC. | 1 | [24](per_fpi/humana_health_benefit_plan_of_louisiana_inc.md) | medicare_advantage |
| `7095adfe-15e7-5c7b-94f5-26dbe123c03b` | SOLIS HEALTH PLANS, INC. | 1 | [24](per_fpi/solis_health_plans_inc.md) | medicare_advantage |
| `4a2ccf0a-b3e0-536e-87fa-29efe11e03e2` | AETNA BETTER HEALTH INC. (GA) | 1 | [22](per_fpi/aetna_better_health_inc_ga.md) | medicare_advantage |
| `6594b1a3-bfdb-5434-b228-09d9cdfa8c87` | AETNA HEALTH INC. (TX) | 1 | [21](per_fpi/aetna_health_inc_tx.md) | medicare_advantage |
| `89c8be9b-7349-579b-9705-36f3a2001746` | DEVOTED HEALTH PLAN OF PENNSYLVANIA INC | 1 | [20](per_fpi/devoted_health_plan_of_pennsylvania_inc.md) | medicare_advantage |
| `2185dc0d-5655-5868-bb26-2f2b9f3d1ef7` | AETNA HEALTH INC. (NY) | 1 | [19](per_fpi/aetna_health_inc_ny.md) | medicare_advantage |
| `1889edb5-077b-572d-8fb4-b79ff8aa6b93` | HUMANA INSURANCE COMPANY OF NEW YORK | 1 | [19](per_fpi/humana_insurance_company_of_new_york.md) | medicare_advantage |
| `e4fa47f0-631d-560c-bfc6-451e1cad518f` | COVENTRY HEALTH CARE OF ILLINOIS, INC. | 1 | [18](per_fpi/coventry_health_care_of_illinois_inc.md) | medicare_advantage |
| `5fc615ed-be1b-5bf3-a4eb-27d4ff983317` | HEALTHSPRING OF FLORIDA, INC. | 1 | [17](per_fpi/healthspring_of_florida_inc.md) | medicare_advantage |
| `8974c38d-3c8c-55a9-950a-2bd583ebb803` | SILVERSCRIPT INSURANCE COMPANY | 1 | [17](per_fpi/silverscript_insurance_company.md) | medicare_advantage |
| `507cee3d-50a3-55b3-a969-03646c4124ab` | AETNA BETTER HEALTH, INC. (LA) | 1 | [16](per_fpi/aetna_better_health_inc_la.md) | medicare_advantage |
| `e4e5f076-bb0d-5c84-94f4-cb8c18de15ab` | DEVOTED HEALTH PLAN OF MISSOURI INC | 1 | [16](per_fpi/devoted_health_plan_of_missouri_inc.md) | medicare_advantage |
| `754c98f1-351b-5f3f-9667-ab3bacb5fbea` | AETNA HEALTH OF CALIFORNIA INC. | 1 | [15](per_fpi/aetna_health_of_california_inc.md) | medicare_advantage |
| `2f3fcf68-c636-5012-ad52-9f3211450103` | DEVOTED HEALTH INSURANCE COMPANY OF INDIANA | 1 | [15](per_fpi/devoted_health_insurance_company_of_indiana.md) | medicare_advantage |
| `32958885-5162-5ce0-9825-16e10c0788fd` | DEVOTED HEALTH PLAN OF ARIZONA, INC. | 1 | [15](per_fpi/devoted_health_plan_of_arizona_inc.md) | medicare_advantage |
| `8c61e19f-0bd3-5a98-8cd3-271dd1f7bf10` | OPTIMUM HEALTHCARE, INC. | 1 | [15](per_fpi/optimum_healthcare_inc.md) | medicare_advantage |
| `5da66e9b-ce78-5082-8152-a09568c8b2cc` | DEVOTED HEALTH INSURANCE COMPANY OF ALABAMA INC | 1 | [13](per_fpi/devoted_health_insurance_company_of_alabama_inc.md) | medicare_advantage |
| `05cfd55b-8d5e-5145-a527-a21e84098252` | DEVOTED HEALTH INSURANCE COMPANY OF TENNESSEE INC | 1 | [13](per_fpi/devoted_health_insurance_company_of_tennessee_inc.md) | medicare_advantage |
| `68fb8eda-430d-5ed8-8c8f-ad9c7637622b` | HEALTHSUN HEALTH PLANS, INC. | 1 | [13](per_fpi/healthsun_health_plans_inc.md) | medicare_advantage |
| `bf7bfdf7-04bd-5f57-b4cc-ecb27fc7d519` | AETNA HEALTH OF MICHIGAN INC. | 1 | [12](per_fpi/aetna_health_of_michigan_inc.md) | medicare_advantage |
| `ddc85dae-3efa-5103-babf-17478c5de2c8` | BLUE CROSS AND BLUE SHIELD OF ALABAMA | 1 | [12](per_fpi/blue_cross_and_blue_shield_of_alabama.md) | medicare_advantage |
| `b908311c-8e05-53c7-b019-40494a62e4e7` | ALLINA HEALTH AND AETNA INSURANCE COMPANY | 1 | [11](per_fpi/allina_health_and_aetna_insurance_company.md) | medicare_advantage |
| `65323ac1-2b45-5f83-a007-a083f42c575c` | DEVOTED HEALTH INSURANCE COMPANY OF GEORGIA INC | 1 | [11](per_fpi/devoted_health_insurance_company_of_georgia_inc.md) | medicare_advantage |
| `035e7476-fa9f-5bee-a59b-099bd8a06c6b` | HEALTH FIRST HEALTH PLANS | 1 | [11](per_fpi/health_first_health_plans.md) | medicare_advantage |
| `403f9e0b-44e0-534f-a69e-c0567e9f74cc` | HEALTHSPRING HEALTHCARE OF COLORADO, INC. | 1 | [11](per_fpi/healthspring_healthcare_of_colorado_inc.md) | medicare_advantage |
| `b94f5c6b-d1c3-5620-8063-34b357d62be6` | HUMANA EMPLOYERS HEALTH PLAN OF GEORGIA, INC. | 1 | [11](per_fpi/humana_employers_health_plan_of_georgia_inc.md) | medicare_advantage |
| `a873e80c-486e-5bd1-be31-08b0e1b67d29` | AETNA BETTER HEALTH OF CALIFORNIA INC. | 1 | [10](per_fpi/aetna_better_health_of_california_inc.md) | medicare_advantage |
| `a9098bc2-d68f-5d8c-823e-7f0bd3b55c33` | AETNA HEALTH INC. (CT) | 1 | [10](per_fpi/aetna_health_inc_ct.md) | medicare_advantage |
| `85e24fd8-c6cb-5445-b1b2-b2b334b2ecee` | AETNA HEALTH INC. (GA) | 1 | [10](per_fpi/aetna_health_inc_ga.md) | medicare_advantage |
| `16408b81-e18a-51bf-b674-6f4f908d4946` | AULTCARE HEALTH INSURING CORPORATION | 1 | [10](per_fpi/aultcare_health_insuring_corporation.md) | medicare_advantage |
| `2e4b484d-9adf-5334-85ff-8a9b1d383f30` | COVENTRY HEALTH CARE OF KANSAS, INC. | 1 | [10](per_fpi/coventry_health_care_of_kansas_inc.md) | medicare_advantage |
| `633d906f-ef04-53e2-b5ab-79aeab24468e` | DEVOTED HEALTH PLAN OF VIRGINIA INC | 1 | [10](per_fpi/devoted_health_plan_of_virginia_inc.md) | medicare_advantage |
| `7d8ddff2-1580-5419-831b-e21c01acaa67` | Devoted of Illinois, Inc. | 1 | [10](per_fpi/devoted_of_illinois_inc.md) | medicare_advantage |
| `f370786a-80f8-5f3d-be28-8791ae273078` | HUMANA MEDICAL PLAN OF MICHIGAN, INC. | 1 | [10](per_fpi/humana_medical_plan_of_michigan_inc.md) | medicare_advantage |
| `5ce212f9-c449-5593-817f-b57a1bc8c0fc` | BRAVO HEALTH MID-ATLANTIC, INC. | 1 | [9](per_fpi/bravo_health_mid_atlantic_inc.md) | medicare_advantage |
| `322ee724-72ab-5119-9c3a-090fac1e4c79` | COVENTRY HEALTH CARE OF NEBRASKA, INC. | 1 | [9](per_fpi/coventry_health_care_of_nebraska_inc.md) | medicare_advantage |
| `47b330a1-1967-5119-bef2-bc8092e84040` | DEVOTED HEALTH INSURANCE COMPANY OF LOUISIANA | 1 | [9](per_fpi/devoted_health_insurance_company_of_louisiana.md) | medicare_advantage |
| `bc3bdf57-1b9b-56bd-9c22-12ebac157a68` | DEVOTED HEALTH PLAN OF COLORADO INC | 1 | [9](per_fpi/devoted_health_plan_of_colorado_inc.md) | medicare_advantage |
| `a02d5a53-39a7-510a-a58c-51b6c0c84dc3` | DEVOTED HEALTH PLAN OF TENNESSEE INC | 1 | [9](per_fpi/devoted_health_plan_of_tennessee_inc.md) | medicare_advantage |
| `e974cafa-6b15-5adf-883c-e848d050a577` | DOCTORS HEALTHCARE PLANS, INC. | 1 | [9](per_fpi/doctors_healthcare_plans_inc.md) | medicare_advantage |
| `c23a1df3-edf2-53b9-bd20-7ef4e653db08` | HUMANA HEALTH COMPANY OF NEW YORK, INC. | 1 | [9](per_fpi/humana_health_company_of_new_york_inc.md) | medicare_advantage |
| `bf05365e-a75b-5020-9d3d-c890824ca792` | AETNA HEALTH INC. (NJ) | 1 | [8](per_fpi/aetna_health_inc_nj.md) | medicare_advantage |
| `5ff2944c-84ae-517d-91fc-244e1cc04754` | BLUE CROSS & BLUE SHIELD OF RHODE ISLAND | 1 | [8](per_fpi/blue_cross_blue_shield_of_rhode_island.md) | medicare_advantage |
| `8b95bdc0-fe69-575b-b22c-c95559f804df` | DEVOTED HEALTH INSURANCE COMPANY OF ARKANSAS INC | 1 | [8](per_fpi/devoted_health_insurance_company_of_arkansas_inc.md) | medicare_advantage |
| `ebd65909-b5fb-5f15-8f77-4277e056dc77` | DEVOTED HEALTH INSURANCE COMPANY OF MISSISSIPPI | 1 | [8](per_fpi/devoted_health_insurance_company_of_mississippi.md) | medicare_advantage |
| `f45a25ad-323b-5278-8fbb-81f06e5f889c` | DEVOTED HEALTH INSURANCE COMPANY OF OKLAHOMA | 1 | [8](per_fpi/devoted_health_insurance_company_of_oklahoma.md) | medicare_advantage |
| `b9bbc9d0-b5b6-58de-9ced-2219dbe118b8` | AETNA HEALTH INC. (ME) | 1 | [7](per_fpi/aetna_health_inc_me.md) | medicare_advantage |
| `e7b1e648-54d9-5aab-ac9f-4afe30ba6713` | DEVOTED HEALTH INSURANCE COMPANY OF HAWAII INC | 1 | [7](per_fpi/devoted_health_insurance_company_of_hawaii_inc.md) | medicare_advantage |
| `22ca301a-6a0f-59df-bb3e-81bce1bfeebe` | DEVOTED HEALTH INSURANCE COMPANY OF KANSAS | 1 | [7](per_fpi/devoted_health_insurance_company_of_kansas.md) | medicare_advantage |
| `e26ac9d7-8dcc-5b4e-9bc7-db9f262c1620` | DEVOTED HEALTH PLAN OF NEW MEXICO, INC. | 1 | [7](per_fpi/devoted_health_plan_of_new_mexico_inc.md) | medicare_advantage |
| `fe9530a4-7cfb-5ed4-8ac5-f82778dce1d4` | HUMANA MEDICAL PLAN OF UTAH, INC. | 1 | [7](per_fpi/humana_medical_plan_of_utah_inc.md) | medicare_advantage |
| `a4af4b81-dfb1-5ad9-a911-9b7caaf7a840` | COVENTRY HEALTH CARE OF WEST VIRGINIA, INC. | 1 | [6](per_fpi/coventry_health_care_of_west_virginia_inc.md) | medicare_advantage |
| `0a80a855-0a9f-57bf-a7f8-08edef7040ad` | DEVOTED HEALTH INSURANCE COMPANY OF KENTUCKY INC | 1 | [6](per_fpi/devoted_health_insurance_company_of_kentucky_inc.md) | medicare_advantage |
| `02c8ec61-997f-55bf-a7b6-3afd0e0ceb5c` | DEVOTED HEALTH INSURANCE COMPANY OF NEBRASKA | 1 | [6](per_fpi/devoted_health_insurance_company_of_nebraska.md) | medicare_advantage |
| `f94faadf-dc7c-5913-b0e4-79a0006ac9cb` | DEVOTED HEALTH INSURANCE COMPANY OF PENNSYLVANIA INC | 1 | [6](per_fpi/devoted_health_insurance_company_of_pennsylvania_inc.md) | medicare_advantage |
| `9c013256-f19d-58d6-b7aa-80db72229e09` | DEVOTED HEALTH INSURANCE COMPANY OF SOUTH CAROLINA INC | 1 | [6](per_fpi/devoted_health_insurance_company_of_south_carolina_inc.md) | medicare_advantage |
| `1ca4c4fb-e462-5f42-b920-b6bc0d4f4ae1` | DEVOTED HEALTH PLAN OF ALABAMA INC | 1 | [6](per_fpi/devoted_health_plan_of_alabama_inc.md) | medicare_advantage |
| `723ebab7-8949-50bd-b901-d82a1996a2e6` | DEVOTED HEALTH PLAN OF OREGON INC | 1 | [6](per_fpi/devoted_health_plan_of_oregon_inc.md) | medicare_advantage |
| `4e1f9c9a-4a2d-548e-8e29-2715878fd2b0` | AETNA BETTER HEALTH OF MICHIGAN INC. | 1 | [5](per_fpi/aetna_better_health_of_michigan_inc.md) | medicare_advantage |
| `239157e0-d4b7-5ba9-96a3-475d8a441317` | DEVOTED HEALTH INSURANCE COMPANY OF ARIZONA, INC. | 1 | [5](per_fpi/devoted_health_insurance_company_of_arizona_inc.md) | medicare_advantage |
| `9c8b98ba-86f6-5919-bbae-7cf23303896a` | DEVOTED HEALTH INSURANCE COMPANY OF COLORADO INC | 1 | [5](per_fpi/devoted_health_insurance_company_of_colorado_inc.md) | medicare_advantage |
| `6a5801e1-c4a0-5d35-b1ca-f057148df32e` | DEVOTED HEALTH INSURANCE COMPANY OF UTAH, INC. | 1 | [5](per_fpi/devoted_health_insurance_company_of_utah_inc.md) | medicare_advantage |
| `695e3531-a115-5077-8326-866a6b90cb67` | DEVOTED HEALTH PLAN OF HAWAII, INC. | 1 | [5](per_fpi/devoted_health_plan_of_hawaii_inc.md) | medicare_advantage |
| `28f84895-a0df-5789-8fa0-4ccd17f7ef0a` | AETNA HEALTH OF UTAH INC. | 1 | [4](per_fpi/aetna_health_of_utah_inc.md) | medicare_advantage |
| `7abfb692-c3d4-5a4a-8592-4c32220da036` | DEVOTED HEALTH INSURANCE COMPANY | 1 | [4](per_fpi/devoted_health_insurance_company.md) | medicare_advantage |
| `62771b6f-ecb7-5e17-b3ff-c80d64022d44` | DEVOTED HEALTH INSURANCE COMPANY OF WASHINGTON | 1 | [4](per_fpi/devoted_health_insurance_company_of_washington.md) | medicare_advantage |
| `bc0ca2f4-ad82-51f6-aab2-bd1bab816f63` | DEVOTED HEALTH PLAN OF ILLINOIS, INC. | 1 | [4](per_fpi/devoted_health_plan_of_illinois_inc.md) | medicare_advantage |
| `194b1292-8aaa-5fad-9e38-5a0a82ea7eb7` | HUMANA HEALTH INSURANCE COMPANY OF FLORIDA, INC. | 1 | [4](per_fpi/humana_health_insurance_company_of_florida_inc.md) | medicare_advantage |
| `5a16d077-9d6b-53c7-92c5-871ffd4263a8` | LEON HEALTH, INC. | 1 | [4](per_fpi/leon_health_inc.md) | medicare_advantage |
| `84f278e3-504c-5402-8e86-1ba33599c3b2` | MEDISUN, INC. | 1 | [4](per_fpi/medisun_inc.md) | medicare_advantage |
| `adfda80f-cea0-5131-a2c3-b31fcd968440` | AETNA BETTER HEALTH OF OKLAHOMA INC. | 1 | [3](per_fpi/aetna_better_health_of_oklahoma_inc.md) | medicare_advantage |
| `e9a3ae68-5f89-594a-b281-6681770b34c2` | AETNA BETTER HEALTH OF TEXAS INC. | 1 | [3](per_fpi/aetna_better_health_of_texas_inc.md) | medicare_advantage |
| `59d7f17c-199b-5831-bcc3-dbf614970edc` | AETNA HEALTH INC. (LA) | 1 | [3](per_fpi/aetna_health_inc_la.md) | medicare_advantage |
| `3ddf9432-6203-5ea4-9c37-89ed4561970f` | DEVOTED HEALTH INSURANCE COMPANY OF DELAWARE | 1 | [3](per_fpi/devoted_health_insurance_company_of_delaware.md) | medicare_advantage |
| `a2eb60a2-b0a4-5e5f-afc9-a03701b251c6` | HUMANA HEALTH PLAN OF OHIO, INC. | 1 | [3](per_fpi/humana_health_plan_of_ohio_inc.md) | medicare_advantage |
| `4d37d600-2a86-5ffc-b03f-83f6f28962a2` | HUMANA INSURANCE COMPANY OF KENTUCKY | 1 | [3](per_fpi/humana_insurance_company_of_kentucky.md) | medicare_advantage |
| `273dc52a-a021-5834-bc9f-1cec607236bf` | VILLAGE SENIOR SERVICES CORPORATION | 1 | [3](per_fpi/village_senior_services_corporation.md) | medicare_advantage |
| `c5363cd3-f131-56e8-8663-1513a99dc168` | AETNA BETTER HEALTH OF WASHINGTON, INC. | 1 | [2](per_fpi/aetna_better_health_of_washington_inc.md) | medicare_advantage |
| `372f7f83-fda9-5388-8ef6-e0d3949548ee` | AETNA HEALTH OF IOWA INC. | 1 | [2](per_fpi/aetna_health_of_iowa_inc.md) | medicare_advantage |
| `bf80a2f0-1372-5b82-b59d-9e594b06c6d6` | AMERICAN HEALTH PLAN OF IOWA INC | 1 | [2](per_fpi/american_health_plan_of_iowa_inc.md) | medicare_advantage |
| `b0095ced-1bb4-51bc-8385-a0921caa67fc` | AMERICAN HEALTH PLAN OF MISSOURI, INC. | 1 | [2](per_fpi/american_health_plan_of_missouri_inc.md) | medicare_advantage |
| `9fd41ef9-9135-5149-8834-26649327492f` | AMERICAN HEALTH PLAN OF UT, INC. | 1 | [2](per_fpi/american_health_plan_of_ut_inc.md) | medicare_advantage |
| `17decc20-4861-5d95-a3b8-5fb0f76aae98` | DEVOTED HEALTH INSURANCE COMPANY OF TEXAS | 1 | [2](per_fpi/devoted_health_insurance_company_of_texas.md) | medicare_advantage |
| `18c004f9-432c-502e-9a96-e6f12382fe84` | DEVOTED HEALTH PLAN OF SOUTH CAROLINA INC | 1 | [2](per_fpi/devoted_health_plan_of_south_carolina_inc.md) | medicare_advantage |
| `95177387-7431-574b-b2d1-476e640503d6` | Devoted Health Insurance Company of Illinois, Inc. | 1 | [2](per_fpi/devoted_health_insurance_company_of_illinois_inc.md) | medicare_advantage |
| `b395801f-73ce-5b52-9a2d-fba3025d2dd6` | FIRST HEALTH LIFE & HEALTH INSURANCE COMPANY | 1 | [2](per_fpi/first_health_life_health_insurance_company.md) | medicare_advantage |
| `d32ed9c3-ef74-5461-9bab-0f9eae374e05` | GEORGIA ASSURANCE, INC. | 1 | [2](per_fpi/georgia_assurance_inc.md) | medicare_advantage |
| `90143b0f-eba0-59c3-8f20-6d814484759e` | HUMANA MEDICAL PLAN OF PENNSYLVANIA, INC. | 1 | [2](per_fpi/humana_medical_plan_of_pennsylvania_inc.md) | medicare_advantage |
| `4b26d8dd-63ba-52a4-9ad1-a45b53e59e60` | HUMANA REGIONAL HEALTH PLAN, INC. | 1 | [2](per_fpi/humana_regional_health_plan_inc.md) | medicare_advantage |
| `92a4d0af-b9f1-5875-a909-4f480828d041` | KANSAS SUPERIOR SELECT, INC. | 1 | [2](per_fpi/kansas_superior_select_inc.md) | medicare_advantage |
| `d795dbb4-7484-5b5b-901d-d8e08110299e` | TEXAS INDEPENDENCE HEALTH PLAN, INC. | 1 | [2](per_fpi/texas_independence_health_plan_inc.md) | medicare_advantage |
| `8931a0c6-113d-543b-b803-19aea57a3a5b` | AETNA BETTER HEALTH INC. (NJ) | 1 | [1](per_fpi/aetna_better_health_inc_nj.md) | medicare_advantage |
| `88c463b7-de36-5ef4-ba70-ac11ce82345d` | AETNA BETTER HEALTH PREMIER PLAN MMAI INC. | 1 | [1](per_fpi/aetna_better_health_premier_plan_mmai_inc.md) | medicare_advantage |
| `d4cc1c53-b225-5a1d-91a5-8dfcaa857b8e` | AMERICAN HEALTH PLAN OF FL, INC. | 1 | [1](per_fpi/american_health_plan_of_fl_inc.md) | medicare_advantage |
| `5755ffb0-3017-53d9-9058-7ea94de8bd89` | AMERICAN HEALTH PLAN OF INDIANA INC | 1 | [1](per_fpi/american_health_plan_of_indiana_inc.md) | medicare_advantage |
| `7e348a76-df96-597a-8f2f-f5d6404a3cc7` | AMERICAN HEALTH PLAN OF MS, INC. | 1 | [1](per_fpi/american_health_plan_of_ms_inc.md) | medicare_advantage |
| `505f12ab-433f-5a92-8cfb-399d59cca50f` | AMERICAN HEALTH PLAN OF PENNSYLVANIA INC | 1 | [1](per_fpi/american_health_plan_of_pennsylvania_inc.md) | medicare_advantage |
| `b7ed99dd-9468-5436-a85c-d3270427b4e5` | AMERICAN HEALTH PLAN OF TX, INC. | 1 | [1](per_fpi/american_health_plan_of_tx_inc.md) | medicare_advantage |
| `b63023c9-a965-55f7-8a2b-056ad8209bf9` | AMERICAN HEALTH PLAN, INC. | 1 | [1](per_fpi/american_health_plan_inc.md) | medicare_advantage |
| `2eee609b-5ea1-5150-8d10-6c3a75530999` | CONTRA COSTA COUNTY MEDICAL SERVICE DBA CONTRA COSTA HEALTH PLAN | 1 | [1](per_fpi/contra_costa_county_medical_service_dba_contra_costa_health_plan.md) | medicare_advantage |
| `6f73024f-18ea-5ae7-a052-c4ff2ae8418f` | COVENTRY HEALTH CARE OF VIRGINIA, INC. | 1 | [1](per_fpi/coventry_health_care_of_virginia_inc.md) | medicare_advantage |
| `5e7c4202-867b-5e28-a3ba-4fbf0da51207` | DEVOTED HEALTH  PLAN OF OREGON | 1 | [1](per_fpi/devoted_health_plan_of_oregon.md) | medicare_advantage |
| `8a699c8d-76ac-51a3-b4d0-3d8e3904e065` | DIGNITY CARE CORPORATION | 1 | [1](per_fpi/dignity_care_corporation.md) | medicare_advantage |
| `817d7c5c-5c06-591b-8fa6-d4690d187e7b` | HEALTHFIRST INSURANCE COMPANY, INC. | 1 | [1](per_fpi/healthfirst_insurance_company_inc.md) | medicare_advantage |
| `bb88e1b4-765e-5b33-8791-6473b0f05c57` | HUMANA BENEFIT PLAN OF SOUTH CAROLINA, INC. | 1 | [1](per_fpi/humana_benefit_plan_of_south_carolina_inc.md) | medicare_advantage |
| `4e82d4d0-2aeb-5382-8d5a-96afe91bc600` | HUMANA HEALTH PLAN OF TEXAS, INC. | 1 | [1](per_fpi/humana_health_plan_of_texas_inc.md) | medicare_advantage |
| `1c9261fc-d3bf-5354-bf3e-73d25816d551` | HUMANA HEALTH PLAN, INC. | 1 | [1](per_fpi/humana_health_plan_inc.md) | medicare_advantage |
| `9db17236-2823-5fe2-bd3f-80c84b22b8e9` | INDEPENDENT CARE HEALTH PLAN | 1 | [1](per_fpi/independent_care_health_plan.md) | medicare_advantage |
| `9fa67da3-c06c-562e-8fad-d7770a8b6088` | Inland Empire Health Plan | 1 | [1](per_fpi/inland_empire_health_plan.md) | medicare_advantage |
| `5b7573d8-88e4-5ff2-88db-6a90aba8d7c5` | LOCAL INITIATIVE HEALTH AUTHORITY FOR LA COUNTY | 1 | [1](per_fpi/local_initiative_health_authority_for_la_county.md) | medicare_advantage |
| `94cd992c-41f6-5b1d-85a5-014ba7f203ac` | OKLAHOMA SUPERIOR SELECT, INC. | 1 | [1](per_fpi/oklahoma_superior_select_inc.md) | medicare_advantage |
| `a2a1901a-a891-5fbb-a099-b220f9d1251f` | SANTA CLARA COUNTY HEALTH AUTHORITY | 1 | [1](per_fpi/santa_clara_county_health_authority.md) | medicare_advantage |

