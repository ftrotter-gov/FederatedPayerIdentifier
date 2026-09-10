# Overlay HTE Release Format Payer Data

Folds payer endpoint data published in the
[HTE PayerEndpoints release format](https://github.com/ftrotter-gov/HTE_data_release_specifications/blob/main/data_release_specifications/PayerEndpoints.md)
into the well-known payer index files under `payer_index_files/`.

The HTE format is one CSV row per payer endpoint. This tool groups those rows by
payer, finds the matching well-known file, and writes the endpoints into it.

## Usage

```bash
python tools/overlay_HTE_release_format_payer_data/overlay.py \
    --source  raw_data_sources/1up_endpoints/1up_health.PayerEndpoints.csv \
    --mapping raw_data_sources/1up_endpoints/mapping.csv
```

Add `--dry-run` to see what would change without writing anything. Always dry-run
first against a new source file.

## The mapping file

Nothing about the translation is hard-coded in the script. A `mapping.csv` beside
the source data documents it, using a `mapping_type` column to hold four kinds of
row:

| `mapping_type` | Purpose |
| -------------- | ------- |
| `column` | One row per HTE column, naming its destination and transform (including the columns deliberately ignored). |
| `enumeration_approach` | Source enumeration label to payer identifier system id, e.g. `NAIC` to `NAIC_ID`. |
| `endpoint_type` | Source `fhir_url_type` to the `plan_endpoints` key to write. |
| `payer_override` | Human-reviewed decisions about specific payers, such as a legal name known not to match. |

A different HTE-format release should get its own mapping file rather than
edits to this script.

## How a row finds its payer

1. **By `payer_lbn`**, normalized through `FPI_maker_cli.normalize_legal_name`
   and compared against each file's `payerLegalName`. This is the primary path.
2. **By `(enumeration_approach, payer_id)`** against crosswalk identifiers
   already in the index. This only works where the index already carries an
   identifier in that system, which today is rare.
3. Otherwise the payer is reported as unmatched and nothing is written.

Rows with neither a legal name nor a payer id are skipped with a warning.

Because real files are inconsistent about repeating `payer_lbn` on every row, a
legal name found on any row of a given `payer_id` is backfilled onto its
siblings before matching. Without that, the blank-name rows would look like a
separate payer and the tool would not be idempotent.

## Writing endpoints

For each endpoint the tool compares against what is already recorded for that
endpoint *family*, ignoring version suffixes, so the seeder's
`davinci_pdex_provider_directory_endpoint#1.1` is recognised as the same
endpoint as a bare `davinci_pdex_provider_directory_endpoint` from the source.

| Situation | Behaviour |
| --------- | --------- |
| Endpoint absent | Added. |
| Endpoint present, same URL | Left alone. This is what makes re-runs idempotent. |
| Endpoint present, different URL | Added under `<key>#conflict_N`; top-level `has_conflict` set to `true`. Neither value is discarded. |
| Sandbox URL | Written under `<key>#sandbox`. Never conflict-tracked: a contradictory sandbox value is warned about and ignored. |

`documentation_url` is mapped onto the existing `ndh_meta_documentation_url`
key. `fhir_url_vendor`, `swagger_url`, `open_api_url`, and `well_known_url` have
no home in the format yet and are ignored; see `FutureSteps.md`.

## Lifecycle

Every file this tool writes is marked `is_seeded: false`, which is what stops
`tools/seed_medicare_advantage/seed.py` from overwriting the overlaid data on a
later run. The FPI is unchanged, so files are edited in place rather than
renamed.

Re-running the tool is safe and produces no changes on the second pass.
