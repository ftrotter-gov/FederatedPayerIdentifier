# Historical Specification: Well-Known JSON Seed Generator

> **Implementation note:** This document records the original seeding request.
> Where it conflicts with the current implementation or current project
> documentation, follow `tools/seed_medicare_advantage/seed.py`,
> `GeneratingFederatedPayerIdentifiers.md`, and `WellKnownFileFormat.md`.
> In particular, the original one-file-per-contract and contract-derived FPI
> directions below have been superseded.

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

Note: the column with the Contract ID and the Payer Name is "Contract ID"
And the contents of this column are "{CONTRACT_ID} - {Payer Name}"

The endpoint column may contain either a single URL or multiple URLs separated by spaces.

For this implementation, ignore any records whose response format is **machine-readable JSON**. Only process the remaining endpoint records.

### 2. Plan Crosswalk

This file contains mappings between Medicare contracts, plans, and payer identifiers.

Although the file contains both previous-year and current-year contract information, only the **current** contract information should be used.

For each record, extract:

* Medicare payer identifier CURRENT_CONTRACT_ID
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

Consolidate contracts that source data associates with the same normalized
payer name into one seeded payer file. This is a temporary seeding compromise,
not a permanent assertion that payer name defines legal identity.

Generate one well-known JSON file for each consolidated seeded payer.
The folder to store these is /payer_index_files/medicare_advantage
Use a "safe name replacement" to create the directory name from the company name, like.. for "METROPLUS HEALTH PLAN, INC." you would write 
/payer_index_files/medicare_advantage/metroplus_health_plan_inc/ 
switch everything to lower case, replace spaces with underscore and remove all special characters for the directory name.

The filename is the safe payer name followed by the generated seeded FPI.
Multiple contract identifiers for the same consolidated payer belong in that
file's identifier and plan data rather than producing one FPI per contract.

```bash
/payer_index_files/medicare_advantage/metroplus_health_plan_inc/metroplus_health_plan_inc_cb562654-b244-4b46-ad06-163105a82e1d.well_known_payer.json
```

The generated record must set `is_seeded` to `true`. A person or curation
process that enriches the record must set it to `false`. Once a payer directory
contains curated content, this general-purpose seeder must not overwrite it.

The output should conform to the well-known JSON format documented WellKnownFileFormat.md 
Most fields articulated in that example will not be available. There will only be one endpoint type we can extract: "davinci_pdex_provider_directory_endpoint#1.1"

The generated output should be minimal, containing only the routing blocks required to represent the distinct endpoint configurations for that payer.

For seed data only, derive the temporary FPI from `LEGAL_NAME_HASH` by importing
the shared generation function from `tools/FPI_maker_cli.py`. Do not duplicate
UUID generation logic in the seeder and do not default to `CMS_CONTRACT_ID`.
Contracts identify contracts, not necessarily the legal payer entity holding
assets and liability for the beneficiary population.

```python

from FPI_maker_cli import generate_fpi

this_payers_fpi = generate_fpi(
    system_id="LEGAL_NAME_HASH",
    payer_id_value="METROPLUS HEALTH PLAN, INC.",
)

```

Add each Medicare Advantage contract ID to the payer identifier list using the
current `CMS_CONTRACT_ID` system URL from
`reference_data/current_payer_identification_systems.json`.

This seeding workflow does not select the payer's permanent FPI. The payer may
later self-issue a random UUID or a UUIDv5 based on any supported identifier it
chooses. Different source choices are not expected to converge.

Please store the program in tools/seed_medicare_advantage/seed.py
Look for the source files in tools/seed_medicare_advantage/source_data

