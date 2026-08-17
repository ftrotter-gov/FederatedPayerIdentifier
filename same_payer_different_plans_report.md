# Same Payer, Different Plans — Report

_Generated: 2026-08-14 13:51:13_

**Identity rule:** A payer is uniquely identified by its **Federated Payer Identifier (FPI)**. Directory names are for human convenience only. The same FPI appearing in **multiple files** is the intended design when a payer has plans with different endpoint sets — each file covers one distinct endpoint configuration. Plans sharing the same endpoint set belong in the same `plan_group` within a single file.

## Summary

| Metric | Count |
|--------|------:|
| Total payer files scanned | 174 |
| Files successfully parsed | 174 |
| Unique FPIs (distinct payers) | 174 |
| **FPIs appearing in multiple files** (same payer, different endpoint sets) | **0** |
| FPIs appearing in exactly one file | 174 |
| Files missing an FPI | 0 |
| Parse errors | 0 |

## Distribution: Number of Files per FPI (Payer)

Each row shows how many payers (FPIs) have exactly N files. Payers with N > 1 are the 'same payer, different plans' cases.

| Files per FPI | # Payers | Notes |
|-------------:|---------:|-------|
| 1 | 174 | all plans share the same endpoint set |

## Same Payer, Different Plans (FPIs in Multiple Files)

_No FPI currently appears in more than one file. This means every payer's plans currently share identical endpoint sets (all plans are in a single file per payer). This is valid — it simply means no payer yet has plans requiring distinct endpoint configurations._

## Single-File Payers (All Plans Share One Endpoint Set)

These **174 payers** each have exactly one file, meaning all their plans currently share the same endpoint configuration.

| FPI | Payer Legal Name | # Endpoint Groups | # Plan IDs | Category |
|-----|-----------------|----------------:|----------:|----------|
| `d9405880-4fc3-5be2-86ba-113f1b0ca0d0` | HUMANA INSURANCE COMPANY | 1 | 264 | medicare_advantage |
| `21d751b4-5010-502f-be61-a33f05c5a139` | AETNA LIFE INSURANCE COMPANY | 1 | 200 | medicare_advantage |
| `784f1b14-40c9-5962-9c7c-874747a67733` | EMPHESYS INSURANCE COMPANY | 1 | 115 | medicare_advantage |
| `80799af7-bae2-51fd-a601-4a6665be5a7f` | HUMANA MEDICAL PLAN, INC. | 1 | 108 | medicare_advantage |
| `0317a046-19e3-59f3-857c-2ae8fa5168f3` | DEVOTED HEALTH PLAN OF FLORIDA, INC. | 1 | 72 | medicare_advantage |
| `6590de98-2615-5aaf-91a6-2f6953e4bec3` | ARCADIAN HEALTH PLAN, INC. | 1 | 71 | medicare_advantage |
| `e6e04792-1dbb-518f-a14b-47d33dffd3e3` | HUMANA WI HEALTH ORGANIZATION INSURANCE CORP | 1 | 53 | medicare_advantage |
| `16cb44ea-1f90-501b-9caa-feafe5d40245` | HEALTHSPRING LIFE & HEALTH INSURANCE COMPANY, INC. | 1 | 52 | medicare_advantage |
| `4fea0378-7e6e-58f2-b0d7-6928a562a92d` | AETNA HEALTH INC. (FL) | 1 | 51 | medicare_advantage |
| `bbf6420c-5d86-5955-bab1-cc536388ca7c` | CARITEN HEALTH PLAN INC. | 1 | 50 | medicare_advantage |
| `8848ad8e-9607-5ad6-8c18-53613444cb2f` | CHA HMO, INC. | 1 | 46 | medicare_advantage |
| `85b47805-905f-54ad-9451-6b265a36baf3` | HUMANA BENEFIT PLAN OF ILLINOIS, INC. | 1 | 46 | medicare_advantage |
| `f69d4ccb-664d-556f-9999-3790e7507ebe` | COVENTRY HEALTH AND LIFE INSURANCE COMPANY | 1 | 38 | medicare_advantage |
| `76e4858e-dc7f-5e06-9040-6fcc36a69f68` | AETNA LIFE INSURANCE COMPANY | 1 | 36 | medicare_advantage |
| `2a397ab0-d659-5d9c-ae26-f5c92c1dbd2a` | CAREPLUS HEALTH PLANS, INC. | 1 | 33 | medicare_advantage |
| `505be802-f9be-513d-86f4-bdef65cf82a9` | COVENTRY HEALTH CARE OF MISSOURI, INC. | 1 | 33 | medicare_advantage |
| `28958e57-8a69-5191-a4d0-d8c6b3c60470` | HUMANA INSURANCE COMPANY | 1 | 33 | medicare_advantage |
| `8321f0a1-da7e-57d8-b232-8efcdf2e454b` | AETNA HEALTH INC. (PA) | 1 | 32 | medicare_advantage |
| `041c92fd-9756-526b-801f-b347a806e3f6` | DEVOTED HEALTH PLAN OF TEXAS, INC. | 1 | 32 | medicare_advantage |
| `5dad5aa1-eb92-53d3-883a-108bc5b13f11` | HEALTHSPRING LIFE & HEALTH INSURANCE COMPANY, INC. | 1 | 32 | medicare_advantage |
| `3ea0309c-64f5-5c73-a82d-f2fc64c3851d` | AETNA HEALTH INC. (PA) | 1 | 28 | medicare_advantage |
| `a8b0616b-285b-5914-b130-997330b2a310` | HEALTHSPRING LIFE & HEALTH INSURANCE COMPANY, INC. | 1 | 28 | medicare_advantage |
| `c0c46331-2d38-5206-9a1b-3cd0aecf1d99` | AETNA HEALTH OF OHIO INC. | 1 | 26 | medicare_advantage |
| `4834a931-9a40-56b7-8930-e22a6dcbdb1c` | AETNA HEALTH AND LIFE INSURANCE COMPANY | 1 | 25 | medicare_advantage |
| `5c8e32af-1889-5b51-96df-cae834fd964c` | FREEDOM HEALTH, INC. | 1 | 25 | medicare_advantage |
| `6f390da5-2c52-5157-9e68-47df08152414` | HUMANA HEALTH BENEFIT PLAN OF LOUISIANA, INC. | 1 | 24 | medicare_advantage |
| `efd86fba-39d0-5c04-86cd-8d0cf9d07562` | MMM HEALTHCARE, LLC | 1 | 24 | medicare_advantage |
| `17ed946c-b2ca-5d1b-9e1d-e1b384b86958` | SOLIS HEALTH PLANS, INC. | 1 | 24 | medicare_advantage |
| `5e4c4d18-0725-58ce-9477-d8482ea11016` | AETNA BETTER HEALTH INC. (GA) | 1 | 22 | medicare_advantage |
| `9811cc74-389d-5c50-9451-6b69c8cd9497` | AETNA HEALTH INC. (TX) | 1 | 20 | medicare_advantage |
| `313aa790-fcee-5858-80df-70ced40ca148` | DEVOTED HEALTH PLAN OF PENNSYLVANIA INC | 1 | 20 | medicare_advantage |
| `9d995d0d-d592-5579-a0a2-c44433b639f7` | HEALTHSPRING LIFE & HEALTH INSURANCE COMPANY, INC. | 1 | 20 | medicare_advantage |
| `d7b76c9d-a218-510e-a079-3b088699d3b5` | MMM HEALTHCARE, LLC | 1 | 20 | medicare_advantage |
| `fcda92db-3ef0-5912-b7ad-433faea3e689` | AETNA HEALTH INC. (NY) | 1 | 19 | medicare_advantage |
| `fc49dd97-5b50-58ca-9c41-2c338feb7547` | HUMANA INSURANCE COMPANY OF NEW YORK | 1 | 19 | medicare_advantage |
| `7f1b0066-bc68-5657-99b2-d2f9cb000b22` | HEALTHSPRING OF FLORIDA, INC. | 1 | 17 | medicare_advantage |
| `7614c716-c49f-5f23-b55d-e7a556fc4056` | SILVERSCRIPT INSURANCE COMPANY | 1 | 17 | medicare_advantage |
| `785cdf96-cbc6-5ffc-a884-39fc2bc6c944` | AETNA BETTER HEALTH, INC. (LA) | 1 | 16 | medicare_advantage |
| `51ce97fc-f9c5-5499-9510-ca799cddf130` | CALIFORNIA PHYSICIANS' SERVICE | 1 | 16 | medicare_advantage |
| `103703b9-f0b4-5d62-81b9-172ffa85b5ca` | DEVOTED HEALTH PLAN OF MISSOURI INC | 1 | 16 | medicare_advantage |
| `5fdd4ea3-fb1a-5ead-b109-8586295d802a` | DEVOTED HEALTH PLAN OF OHIO, INC. | 1 | 16 | medicare_advantage |
| `130b237f-e93c-5ade-95ae-d63143cb9bfa` | AETNA HEALTH OF CALIFORNIA INC. | 1 | 15 | medicare_advantage |
| `0edc0d00-b61d-5003-992e-4f4c4e3127b2` | DEVOTED HEALTH INSURANCE COMPANY OF INDIANA | 1 | 15 | medicare_advantage |
| `f03d1beb-a479-5f90-bf7b-9ff065def2d3` | DEVOTED HEALTH PLAN OF ARIZONA, INC. | 1 | 15 | medicare_advantage |
| `0446e340-9e2c-532b-84ca-6a4e929844a0` | OPTIMUM HEALTHCARE, INC. | 1 | 15 | medicare_advantage |
| `8b1ba2f7-7873-5529-bd5d-45f9865044fe` | BRAVO HEALTH PENNSYLVANIA, INC. | 1 | 13 | medicare_advantage |
| `dc77923c-df26-53b3-9504-39537ef3a72c` | DEVOTED HEALTH INSURANCE COMPANY OF ALABAMA INC | 1 | 13 | medicare_advantage |
| `a4bd3a32-a4aa-568c-8426-c90522dbf49e` | DEVOTED HEALTH INSURANCE COMPANY OF TENNESSEE INC | 1 | 13 | medicare_advantage |
| `b68b5ecb-2fe8-5c3b-8e4a-9897262bc870` | HEALTHSUN HEALTH PLANS, INC. | 1 | 13 | medicare_advantage |
| `dffdeb6e-9113-5ad7-9018-0553afb93367` | AETNA HEALTH OF MICHIGAN INC. | 1 | 12 | medicare_advantage |
| `dde68f02-0911-5232-af8a-2ede2f0bb3ac` | BLUE CROSS AND BLUE SHIELD OF ALABAMA | 1 | 12 | medicare_advantage |
| `99b96b9d-fb0b-5c3e-bba9-3dd6921caa0a` | COVENTRY HEALTH CARE OF ILLINOIS, INC. | 1 | 12 | medicare_advantage |
| `61fdf22f-08af-5814-83db-a2a3a6ca1eff` | ALLINA HEALTH AND AETNA INSURANCE COMPANY | 1 | 11 | medicare_advantage |
| `a16a1880-454b-5e17-974b-b19cd949c686` | BRAVO HEALTH PENNSYLVANIA, INC. | 1 | 11 | medicare_advantage |
| `038f4c81-2e24-590c-9336-b42e190cdb33` | DEVOTED HEALTH INSURANCE COMPANY OF GEORGIA INC | 1 | 11 | medicare_advantage |
| `10f03a8e-67b7-5cb2-8ea2-777f45c2ea8a` | DEVOTED HEALTH PLAN OF NORTH CAROLINA INC | 1 | 11 | medicare_advantage |
| `20f0e679-06e0-5013-a362-250d34f812b5` | HEALTH FIRST HEALTH PLANS | 1 | 11 | medicare_advantage |
| `19621e6f-cf0a-554e-9ced-82281b9c1493` | HEALTHSPRING HEALTHCARE OF COLORADO, INC. | 1 | 11 | medicare_advantage |
| `b11d538a-aa95-5c89-b619-313997a875dd` | HUMANA EMPLOYERS HEALTH PLAN OF GEORGIA, INC. | 1 | 11 | medicare_advantage |
| `44f0be88-1771-56d6-adc4-54537fb53619` | HUMANA INSURANCE COMPANY | 1 | 11 | medicare_advantage |
| `2ccb3549-b7ab-5838-add4-d1740d64e25b` | AETNA BETTER HEALTH OF CALIFORNIA INC. | 1 | 10 | medicare_advantage |
| `462a5604-3ede-567e-81d4-5c01f667199a` | AETNA HEALTH INC. (CT) | 1 | 10 | medicare_advantage |
| `f0a7f6d8-b243-5d7c-9b2a-f610e1ae07b2` | AULTCARE HEALTH INSURING CORPORATION | 1 | 10 | medicare_advantage |
| `0aff743e-5d99-5053-8f48-152824f6378d` | COVENTRY HEALTH CARE OF KANSAS, INC. | 1 | 10 | medicare_advantage |
| `6b83c35d-4516-5f7c-b64f-fba922a82cae` | DEVOTED HEALTH PLAN OF VIRGINIA INC | 1 | 10 | medicare_advantage |
| `7a57a066-eae6-5e6c-8399-3b440c04da43` | Devoted of Illinois, Inc. | 1 | 10 | medicare_advantage |
| `db73a1fc-7a1d-5048-af2b-d8bf88d92705` | BRAVO HEALTH MID-ATLANTIC, INC. | 1 | 9 | medicare_advantage |
| `a1ebb509-de83-5016-b7a7-6103e9e88e0d` | COVENTRY HEALTH CARE OF NEBRASKA, INC. | 1 | 9 | medicare_advantage |
| `690aa4cd-8fba-5d4a-8313-9d75392a0c8c` | DEVOTED HEALTH INSURANCE COMPANY OF LOUISIANA | 1 | 9 | medicare_advantage |
| `7ab9e2f6-7d70-5e5d-aedb-f52ba754f454` | DEVOTED HEALTH PLAN OF COLORADO INC | 1 | 9 | medicare_advantage |
| `4937a55e-459c-538d-a42f-44fd837c0624` | DEVOTED HEALTH PLAN OF NORTH CAROLINA INC | 1 | 9 | medicare_advantage |
| `93652d6e-f7b3-535f-b2c5-75338283f7b4` | DEVOTED HEALTH PLAN OF TENNESSEE INC | 1 | 9 | medicare_advantage |
| `bcc04a53-ff75-5622-a67a-fca5062c3510` | DOCTORS HEALTHCARE PLANS, INC. | 1 | 9 | medicare_advantage |
| `de29d46b-e9fb-5f51-ad26-5f7bad38221e` | HUMANA HEALTH COMPANY OF NEW YORK, INC. | 1 | 9 | medicare_advantage |
| `e956f341-081d-5eb3-ae93-5ba9d7f0e600` | HUMANA MEDICAL PLAN OF MICHIGAN, INC. | 1 | 9 | medicare_advantage |
| `d2ac0ba0-e4fb-5bbf-a39e-3b3d8c1aa4ab` | AETNA HEALTH INC. (NJ) | 1 | 8 | medicare_advantage |
| `d4641577-31e1-5977-a424-015e597c7c0d` | BLUE CROSS & BLUE SHIELD OF RHODE ISLAND | 1 | 8 | medicare_advantage |
| `5768944b-363f-5a16-a866-25bcc3d0bb39` | DEVOTED HEALTH INSURANCE COMPANY OF ARKANSAS INC | 1 | 8 | medicare_advantage |
| `9bc8e572-5514-5766-9fe4-2b380b0f57f3` | DEVOTED HEALTH INSURANCE COMPANY OF MISSISSIPPI | 1 | 8 | medicare_advantage |
| `2efeeb97-a4ff-5455-9c08-ad3e4f48db15` | DEVOTED HEALTH INSURANCE COMPANY OF OKLAHOMA | 1 | 8 | medicare_advantage |
| `1ac97502-7c05-5a7e-a52f-70647697b8c5` | HEALTHSPRING LIFE & HEALTH INSURANCE COMPANY, INC. | 1 | 8 | medicare_advantage |
| `7d970c9b-f2e3-5e2b-afe9-72744454e9da` | HUMANA BENEFIT PLAN OF ILLINOIS, INC. | 1 | 8 | medicare_advantage |
| `23d42cb8-f4db-5a3a-96ef-6f823a9433ee` | AETNA HEALTH INC. (GA) | 1 | 7 | medicare_advantage |
| `9aebe8e0-9c60-5e92-b961-5560bda9bbc4` | AETNA HEALTH INC. (ME) | 1 | 7 | medicare_advantage |
| `c47dfd94-4212-51a5-b308-57fabdbd1704` | BRAVO HEALTH PENNSYLVANIA, INC. | 1 | 7 | medicare_advantage |
| `0fca6c77-60b6-5ed4-8c5b-4c3654de435b` | DEVOTED HEALTH INSURANCE COMPANY OF HAWAII INC | 1 | 7 | medicare_advantage |
| `18261002-e56e-54f4-a6f0-a6ef0bcc5b65` | DEVOTED HEALTH INSURANCE COMPANY OF KANSAS | 1 | 7 | medicare_advantage |
| `034e27f9-c675-5494-8294-f17124463073` | DEVOTED HEALTH PLAN OF NEW MEXICO, INC. | 1 | 7 | medicare_advantage |
| `4fc6ff8b-e3fe-5cb4-83a6-9bd2a7b4b808` | HEALTHFIRST HEALTH PLAN, INC. | 1 | 7 | medicare_advantage |
| `99c463a0-db60-53ae-9022-380383cdab9d` | HUMANA MEDICAL PLAN OF UTAH, INC. | 1 | 7 | medicare_advantage |
| `c5e03f3d-5978-5c39-8ff0-82cd598a97e7` | COVENTRY HEALTH CARE OF ILLINOIS, INC. | 1 | 6 | medicare_advantage |
| `8ac8827f-8f2f-55c2-a056-61cbdbe7a43b` | COVENTRY HEALTH CARE OF WEST VIRGINIA, INC. | 1 | 6 | medicare_advantage |
| `f262cb98-d199-567f-a5f0-bcfca9ce3714` | DEVOTED HEALTH INSURANCE COMPANY OF KENTUCKY INC | 1 | 6 | medicare_advantage |
| `8e8a31e5-606a-5c28-b242-ea141e998e11` | DEVOTED HEALTH INSURANCE COMPANY OF NEBRASKA | 1 | 6 | medicare_advantage |
| `cebd9851-baaf-5683-8964-0f33a955daa5` | DEVOTED HEALTH INSURANCE COMPANY OF PENNSYLVANIA INC | 1 | 6 | medicare_advantage |
| `4f535fdb-9bfa-50bf-82c0-33902a77f99f` | DEVOTED HEALTH INSURANCE COMPANY OF SOUTH CAROLINA INC | 1 | 6 | medicare_advantage |
| `e5479f42-772d-509a-b590-55ff58564bbf` | DEVOTED HEALTH PLAN OF ALABAMA INC | 1 | 6 | medicare_advantage |
| `f6106b1d-2d70-5df3-a5f1-eb302c77c0ca` | DEVOTED HEALTH PLAN OF OREGON INC | 1 | 6 | medicare_advantage |
| `2400dd70-5fe6-5c67-b9bd-7066631dbb46` | HUMANA WI HEALTH ORGANIZATION INSURANCE CORP | 1 | 6 | medicare_advantage |
| `856df8cb-529f-582f-89ff-044d65c782bf` | DEVOTED HEALTH INSURANCE COMPANY OF ARIZONA, INC. | 1 | 5 | medicare_advantage |
| `4b55d481-9cc0-54aa-9548-bb24e0badb04` | DEVOTED HEALTH INSURANCE COMPANY OF COLORADO INC | 1 | 5 | medicare_advantage |
| `81a194af-2255-5f2e-9613-d6ca2e882726` | DEVOTED HEALTH INSURANCE COMPANY OF UTAH, INC. | 1 | 5 | medicare_advantage |
| `370e89e0-0d0f-5a52-9689-580cf1e4f158` | DEVOTED HEALTH PLAN OF HAWAII, INC. | 1 | 5 | medicare_advantage |
| `900f1613-1228-5268-ac17-c83a9746f012` | HUMANA INSURANCE COMPANY | 1 | 5 | medicare_advantage |
| `bc385fa5-b436-51cc-940d-e79cd8648c66` | HUMANA INSURANCE COMPANY | 1 | 5 | medicare_advantage |
| `2b9ca0a2-bd9e-5094-8912-10ae3667eb0d` | AETNA BETTER HEALTH OF MICHIGAN INC. | 1 | 4 | medicare_advantage |
| `8ec70993-95dd-5132-a608-b5578cfc8662` | AETNA HEALTH INC. (PA) | 1 | 4 | medicare_advantage |
| `c285021e-2483-532c-911a-21dedff69c33` | AETNA HEALTH OF UTAH INC. | 1 | 4 | medicare_advantage |
| `d427b6e7-38f0-5101-83d9-7c7dc08d4cfb` | DEVOTED HEALTH INSURANCE COMPANY | 1 | 4 | medicare_advantage |
| `d37de223-3e56-56de-8b81-c2f8a8c127f0` | DEVOTED HEALTH INSURANCE COMPANY OF WASHINGTON | 1 | 4 | medicare_advantage |
| `121a6aa6-e0cd-5cb1-9f81-3b968cfbbd39` | DEVOTED HEALTH PLAN OF ILLINOIS, INC. | 1 | 4 | medicare_advantage |
| `4b72cac0-3d03-5167-bef1-0727e5e2716e` | HEALTHSPRING LIFE & HEALTH INSURANCE COMPANY, INC. | 1 | 4 | medicare_advantage |
| `d304b5fe-a9ec-5d71-9bc4-9ca560d1d92e` | HUMANA HEALTH INSURANCE COMPANY OF FLORIDA, INC. | 1 | 4 | medicare_advantage |
| `1f416841-4e39-5700-9ba1-c482df734e8e` | HUMANA INSURANCE COMPANY | 1 | 4 | medicare_advantage |
| `2d837940-306d-505b-8d71-3f009606641b` | HUMANA INSURANCE COMPANY | 1 | 4 | medicare_advantage |
| `d40c409d-bf0b-50c5-8314-7750c1da4501` | HUMANA INSURANCE COMPANY | 1 | 4 | medicare_advantage |
| `df5c820f-6625-5a5c-8018-d14e7b5199fe` | LEON HEALTH, INC. | 1 | 4 | medicare_advantage |
| `d4ef3a7c-ba4e-5d82-8c15-9b835dfe4f79` | MEDISUN, INC. | 1 | 4 | medicare_advantage |
| `693d4bb0-7b10-5410-8bb6-060ba065e014` | AETNA BETTER HEALTH OF OKLAHOMA INC. | 1 | 3 | medicare_advantage |
| `50764980-451e-509a-a4a3-24f09a5bf9fd` | AETNA BETTER HEALTH OF TEXAS INC. | 1 | 3 | medicare_advantage |
| `c595c822-53a3-5020-8d38-26fcf4360818` | AETNA HEALTH INC. (GA) | 1 | 3 | medicare_advantage |
| `d0e1c7bb-5f90-510a-802a-b3312817b251` | AETNA HEALTH INC. (LA) | 1 | 3 | medicare_advantage |
| `471d3cf6-6fea-5e29-8af6-39d340d9ab65` | ARCADIAN HEALTH PLAN, INC. | 1 | 3 | medicare_advantage |
| `7ba6dc28-44f5-5e95-ac92-70158acee99e` | DEVOTED HEALTH INSURANCE COMPANY OF DELAWARE | 1 | 3 | medicare_advantage |
| `ac16414d-13ae-560c-96d5-92d7ca15f3d0` | DEVOTED HEALTH PLAN OF OHIO INC | 1 | 3 | medicare_advantage |
| `b11dde3a-417c-55cd-8f0b-d613237e90fb` | HUMANA HEALTH PLAN OF OHIO, INC. | 1 | 3 | medicare_advantage |
| `9acacde8-dd50-50f6-abb7-8c4f81ab2b43` | HUMANA INSURANCE COMPANY OF KENTUCKY | 1 | 3 | medicare_advantage |
| `b1cf69c6-c024-5864-a21d-8bae9c435122` | VILLAGE SENIOR SERVICES CORPORATION | 1 | 3 | medicare_advantage |
| `2cfcb8ff-0303-5887-8369-bff838bad33e` | AETNA BETTER HEALTH OF WASHINGTON, INC. | 1 | 2 | medicare_advantage |
| `14ee618f-d694-57ac-a7f7-6972fe78b59f` | AETNA HEALTH INC. (TX) | 1 | 2 | medicare_advantage |
| `ca87b310-8cf1-5906-b9ab-d580eafb8229` | AETNA HEALTH OF IOWA INC. | 1 | 2 | medicare_advantage |
| `ba5ca10c-09b6-5386-a986-bdf98099449a` | AMERICAN HEALTH PLAN OF IOWA INC | 1 | 2 | medicare_advantage |
| `6a6c6467-e730-5d58-b6d4-d2d65be0fba2` | AMERICAN HEALTH PLAN OF MISSOURI, INC. | 1 | 2 | medicare_advantage |
| `cbc3b9ed-ce11-5c51-bd6d-17477c34ddfe` | AMERICAN HEALTH PLAN OF UT, INC. | 1 | 2 | medicare_advantage |
| `2c180a05-3f29-57bb-a439-4d332a693a33` | California Physicians' Service | 1 | 2 | medicare_advantage |
| `107a9753-3955-59a1-9074-35c8d86c516f` | DEVOTED HEALTH INSURANCE COMPANY OF TEXAS | 1 | 2 | medicare_advantage |
| `b267689d-8679-5464-ac99-6cb42815ac7a` | DEVOTED HEALTH PLAN OF SOUTH CAROLINA INC | 1 | 2 | medicare_advantage |
| `e15bbb18-fe35-5c25-a037-342de1a51ac9` | Devoted Health Insurance Company of Illinois, Inc. | 1 | 2 | medicare_advantage |
| `88e1c81c-b8b6-5c0c-ae25-388d04ac9cee` | FIRST HEALTH LIFE & HEALTH INSURANCE COMPANY | 1 | 2 | medicare_advantage |
| `c5d02143-ac0f-53de-832f-e72d7da0e111` | GEORGIA ASSURANCE, INC. | 1 | 2 | medicare_advantage |
| `ab6d09d1-4530-559d-a686-4deef9dfa18c` | HEALTHSPRING LIFE & HEALTH INSURANCE COMPANY, INC. | 1 | 2 | medicare_advantage |
| `0c9c9b30-d5ba-5b09-9d9a-52f26024d149` | HUMANA MEDICAL PLAN OF PENNSYLVANIA, INC. | 1 | 2 | medicare_advantage |
| `0ffa6d37-df9e-5b8c-af22-20b361e3a810` | HUMANA REGIONAL HEALTH PLAN, INC. | 1 | 2 | medicare_advantage |
| `5da8bf7e-82e4-54eb-a9e6-6177ead3f7c3` | KANSAS SUPERIOR SELECT, INC. | 1 | 2 | medicare_advantage |
| `0e700d7a-ab07-5e3b-ba9f-f6256f68c247` | TEXAS INDEPENDENCE HEALTH PLAN, INC. | 1 | 2 | medicare_advantage |
| `f3ad3740-96ea-546c-8cd7-201cbcea578b` | AETNA BETTER HEALTH INC. (NJ) | 1 | 1 | medicare_advantage |
| `2862dd9c-a265-57e1-9984-b9105b712428` | AETNA BETTER HEALTH OF MICHIGAN INC. | 1 | 1 | medicare_advantage |
| `008eae42-9404-5d43-b4f1-c1e04fa02fec` | AETNA BETTER HEALTH PREMIER PLAN MMAI INC. | 1 | 1 | medicare_advantage |
| `c7b69c36-0792-5d58-9a51-73836d215b70` | AETNA LIFE INSURANCE COMPANY | 1 | 1 | medicare_advantage |
| `f40f76a2-3969-51b8-a248-6e1912d44dff` | AMERICAN HEALTH PLAN OF FL, INC. | 1 | 1 | medicare_advantage |
| `12bc87d0-df12-5299-b774-e25d101b4c62` | AMERICAN HEALTH PLAN OF INDIANA INC | 1 | 1 | medicare_advantage |
| `75b2961a-5d6a-552f-8c41-ea9b9eff6819` | AMERICAN HEALTH PLAN OF MS, INC. | 1 | 1 | medicare_advantage |
| `4c184563-ed38-5888-9a5a-c1d42ee87388` | AMERICAN HEALTH PLAN OF PENNSYLVANIA INC | 1 | 1 | medicare_advantage |
| `55a6a297-345f-5b6d-bd07-7fbbdb678a67` | AMERICAN HEALTH PLAN OF TX, INC. | 1 | 1 | medicare_advantage |
| `79d5a923-55c8-5c07-ab08-1400bc947ebc` | AMERICAN HEALTH PLAN, INC. | 1 | 1 | medicare_advantage |
| `13c70d1b-fefd-52e8-a197-d18f2cf9b187` | BRAVO HEALTH PENNSYLVANIA, INC. | 1 | 1 | medicare_advantage |
| `d4b8d6b3-1fb9-5ede-9a50-a00fae97e06a` | CALIFORNIA PHYSICIANS' SERVICE | 1 | 1 | medicare_advantage |
| `b2b5f6e2-9eb5-5552-a00f-dc38a06fcc20` | CONTRA COSTA COUNTY MEDICAL SERVICE DBA CONTRA COSTA HEALTH PLAN | 1 | 1 | medicare_advantage |
| `d91232ca-d0f3-5b46-9b8a-d2aa874907a5` | COVENTRY HEALTH CARE OF VIRGINIA, INC. | 1 | 1 | medicare_advantage |
| `6bed6038-e82c-5073-a51e-51052cd8f276` | DEVOTED HEALTH  PLAN OF OREGON | 1 | 1 | medicare_advantage |
| `647a6061-fa12-5566-91bb-2f3a39619ae2` | DIGNITY CARE CORPORATION | 1 | 1 | medicare_advantage |
| `a7baa401-eeee-5df7-ad54-1e7e258326a6` | HEALTHFIRST HEALTH PLAN, INC. | 1 | 1 | medicare_advantage |
| `b85ef64f-d5b7-58aa-bf40-2cc0906fc339` | HEALTHFIRST HEALTH PLAN, INC. | 1 | 1 | medicare_advantage |
| `c3936200-3c03-53cd-9e3e-73f63fd700ea` | HEALTHFIRST INSURANCE COMPANY, INC. | 1 | 1 | medicare_advantage |
| `fca47aa9-ab0f-5ef8-9ab0-48e3b991d79f` | HUMANA BENEFIT PLAN OF ILLINOIS, INC. | 1 | 1 | medicare_advantage |
| `fde68862-ed6e-5a1b-8a73-97358e551152` | HUMANA BENEFIT PLAN OF SOUTH CAROLINA, INC. | 1 | 1 | medicare_advantage |
| `6e24a052-2e40-5012-bed5-54944af84385` | HUMANA HEALTH PLAN OF TEXAS, INC. | 1 | 1 | medicare_advantage |
| `042c5f58-cb9d-5c6e-ad2f-55259512b744` | HUMANA HEALTH PLAN, INC. | 1 | 1 | medicare_advantage |
| `d5e34207-0788-5ee9-98bd-56a6dc0896dd` | HUMANA MEDICAL PLAN OF MICHIGAN, INC. | 1 | 1 | medicare_advantage |
| `f242d878-56d8-5e7d-804a-f94059653e4e` | INDEPENDENT CARE HEALTH PLAN | 1 | 1 | medicare_advantage |
| `ae95be34-0331-57f7-9d49-2dfc2a29380b` | Inland Empire Health Plan | 1 | 1 | medicare_advantage |
| `24a1e693-971a-5aaf-8131-d18fb05b5495` | LOCAL INITIATIVE HEALTH AUTHORITY FOR LA COUNTY | 1 | 1 | medicare_advantage |
| `ef023a82-a768-5c2c-8551-87f7738b4336` | OKLAHOMA SUPERIOR SELECT, INC. | 1 | 1 | medicare_advantage |
| `6d0a0c4b-2667-5a32-bab0-bef01ddf2093` | SANTA CLARA COUNTY HEALTH AUTHORITY | 1 | 1 | medicare_advantage |

