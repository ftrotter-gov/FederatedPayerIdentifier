# Specification: Well-Known JSON Seed Generator

## Overview

Create a command-line tool that generates a minimal set of well-known JSON files from two CMS source CSV files. The generated files are intended to serve as seed data and should conform to the well-known file format described elsewhere in this repository.

The implementation should begin by reading the example well-known JSON file and the accompanying README that defines the file format.

## Inputs

The program consumes two CSV files.

### 1. Payer URL List

This file contains:

* Contract ID 
* Payer name
* One or more FHIR endpoint URLs
* Response format

Not the column with the Contract ID and the Payer Name is "Contract ID"
And the contents of this column are "{CONTRACT_ID} - {Payer Name}"

The endpoint column may contain either a single URL or multiple URLs separated by spaces.

For this implementation, ignore any records whose response format is **machine-readable JSON**. Only process the remaining endpoint records.

### 2. Plan Crosswalk

This file contains mappings between Medicare contracts, plans, and payer identifiers.

Although the file contains both previous-year and current-year contract information, only the **current** contract information should be used.

For each record, extract:

* Medicare payeridentifier CURRENT_CONTRACT_ID
* Plan ID CURRENT_PLAN_ID
* Plan name CURRENT_PLAN_NAME

The Contract ID is used to join this file with the Payer URL List.

## Processing

Join the two input files using the current Contract ID.

For each payer:

1. Determine the payer's Medicare payer identifier. (CURRENT_CONTRACT_ID) 
2. Associate every plan belonging to that payer.
3. Associate each plan with the FHIR endpoint set obtained from the Payer URL List.

Plans should then be grouped according to their endpoint configuration.

If multiple plans have the identical set of FHIR endpoints, they should be represented within a single routing block in the generated well-known JSON.

If different plans have different endpoint sets, separate routing blocks should be generated.

The uniqueness of a routing block is determined solely by the complete set of FHIR endpoints associated with it.

Each routing block should contain all plan identifiers that resolve to that identical endpoint set.

## Output

Generate one well-known JSON file for each payer contract_id. 
The folder to store these is /payer_index_files/medicare_advantage
Use a "safe name replacement" to create the directory name from the company name, like.. for "METROPLUS HEALTH PLAN, INC." you would write 
/payer_index_files/medicare_advantage/metroplus_health_plan_inc/ 
switch everything to lower case, replace spaces with underscore and remove all special characters for the directory name.

The name of the file should be the same name as the directory, with the generated FPI (which will be different for every contract id.)
So we would expect to see: 

```bash
/payer_index_files/medicare_advantage/metroplus_health_plan_inc/metroplus_health_plan_inc_cb562654-b244-4b46-ad06-163105a82e1d.well_known_payer.json
/payer_index_files/medicare_advantage/metroplus_health_plan_inc/metroplus_health_plan_inc_cb562654-b244-4b46-ad06-163105a82e43.well_known_payer.json
```

Where the two files represent the same company name, but different FPI numbers. 

The output should conform to the well-known JSON format documented WellKnownFileFormat.md 
Most fields articulated in that example will not be available. There will only be one endpoint type we can extract: "davinci_pdex_provider_directory_endpoint#1.1"

The generated output should be minimal, containing only the routing blocks required to represent the distinct endpoint configurations for that payer.

In order to generate the FPI, use uuid5 like this: 

```python

import uuid

parent_namespace = uuid.NAMESPACE_DNS

medicare_advantage_system_uuid = uuid.uuid5(parent_namespace, "CMS_CONTRACT_ID.fhir")

this_payers_FPI = uuid.uuid5(medicare_advantage_system_uuid, '12345')

```

Make sure to also add the medicare advantage contract id under to the identifier list under as:

"system": "http://hl7.org/fhir/us/fast-ndh/NotSure/WhatGoesHere/MedicarePayerIdentifer"

for the initial implementation.

Please store the program in tools/seed_medicare_advantage/seed.py
Look for the source files in tools/seed_medicare_advantage/source_data

