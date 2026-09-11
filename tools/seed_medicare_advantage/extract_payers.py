#!/usr/bin/env python3
"""Roll a CMS "Monthly Report By Plan" CSV up to one row per contract.

The monthly enrollment report published by CMS is a *plan* level file: each row
is one contract/plan-id pair.  There is no contract level summary anywhere in
it, even though every payer-identifying column it carries (organization name,
organization marketing name, parent organization) is in practice a property of
the contract rather than of the individual plan.

This script produces that missing contract level summary, writing these
columns:

    Contract Number              the CMS contract ID (e.g. "H1234", "S5678")
    Plan Count                   count of *distinct*, non-empty Plan ID values
                                 seen for that contract
    Organization Name            the contract's organization (legal) name
    Organization Marketing Name  the contract's marketing name
    Parent Organization          the contract's parent organization

Notes on the rollup
-------------------
* Plan Count counts distinct Plan ID values, not rows.  Blank Plan ID cells
  (cost/HCPP style contracts that have no plan segment) are not counted, so a
  contract can legitimately report a plan count of 0.
* The three name columns are supposed to be constant within a contract.  Where
  the source data disagrees, the most frequent non-empty value wins (ties are
  broken by first appearance in the file) and every disagreement is reported on
  stderr so the inconsistency stays visible rather than being silently
  flattened.
* Output rows are sorted by contract number so that re-running the script
  against the same input produces a byte-identical file.

No file name is hard-coded: both the input and the output CSV must be named on
the command line.

Usage:
    python3 tools/seed_medicare_advantage/extract_payers.py INPUT_CSV OUTPUT_CSV

Example:
    python3 tools/seed_medicare_advantage/extract_payers.py \\
        tools/seed_medicare_advantage/source_data/Monthly_Report_By_Plan_2026_08.csv \\
        tools/seed_medicare_advantage/source_data/payer_by_ma_contract.csv
"""

import argparse
import csv
import os
import sys

# Column names as they appear in the first line of the monthly report CSV.
COL_CONTRACT = "Contract Number"
COL_PLAN_ID = "Plan ID"
COL_ORG_NAME = "Organization Name"
COL_ORG_MARKETING_NAME = "Organization Marketing Name"
COL_PARENT_ORG = "Parent Organization"

# Column names written to the contract level output file.
OUT_COL_CONTRACT = "Contract Number"
OUT_COL_PLAN_COUNT = "Plan Count"

# The name columns rolled up per contract, in output order.
NAME_COLUMNS = (COL_ORG_NAME, COL_ORG_MARKETING_NAME, COL_PARENT_ORG)

# The CMS monthly report is exported from a Windows toolchain and is not valid
# UTF-8: some plan names contain cp1252 punctuation (e.g. 0x96, an en dash).
# Try UTF-8 first (with BOM tolerance) and fall back to cp1252, which decodes
# every byte value and so cannot fail.
SOURCE_ENCODINGS = ("utf-8-sig", "cp1252")


def open_source_csv(filepath):
    """Open the source CSV, trying each supported encoding in turn.

    Returns the open file object.  newline="" lets the csv module handle the
    file's CRLF line endings itself.
    """
    last_error = None
    for encoding in SOURCE_ENCODINGS:
        handle = open(filepath, encoding=encoding, newline="")
        try:
            handle.read()
        except UnicodeDecodeError as exc:
            handle.close()
            last_error = exc
            continue
        handle.seek(0)
        return handle
    raise SystemExit(
        f"ERROR: could not decode {filepath} as any of "
        f"{', '.join(SOURCE_ENCODINGS)}: {last_error}"
    )


def pick_value(counts):
    """Return the most frequent value from a {value: row_count} mapping.

    Python dicts preserve insertion order, so when two values are tied the one
    that appeared first in the source file wins.  An empty mapping (the
    contract never carried a non-empty value in this column) yields "".
    """
    best_value = ""
    best_count = -1
    for value, count in counts.items():
        if count > best_count:
            best_value = value
            best_count = count
    return best_value if best_count > 0 else ""


def load_contracts(filepath):
    """Read the plan level CSV and return (contracts, stats).

    contracts maps contract_id -> a rollup dict holding the set of distinct
    plan IDs seen, a per-column tally of the non-empty name values seen, and
    the number of source rows contributing to the contract.
    """
    contracts = {}
    stats = {"rows": 0, "skipped_no_contract": 0, "rows_without_plan_id": 0}

    # utf-8-sig: the CMS exports are occasionally BOM-prefixed.  The file is
    # CRLF terminated, so newline="" lets the csv module handle line endings.
    with open_source_csv(filepath) as f:
        reader = csv.DictReader(f)

        fieldnames = reader.fieldnames or []
        missing = [
            c
            for c in (COL_CONTRACT, COL_PLAN_ID, *NAME_COLUMNS)
            if c not in fieldnames
        ]
        if missing:
            raise SystemExit(
                f"ERROR: {filepath} is missing expected column(s): "
                + ", ".join(missing)
            )

        for row in reader:
            stats["rows"] += 1

            contract_id = (row.get(COL_CONTRACT) or "").strip()
            if not contract_id:
                stats["skipped_no_contract"] += 1
                continue

            entry = contracts.get(contract_id)
            if entry is None:
                entry = {
                    "plan_ids": set(),
                    "row_count": 0,
                    "names": {col: {} for col in NAME_COLUMNS},
                }
                contracts[contract_id] = entry

            entry["row_count"] += 1

            plan_id = (row.get(COL_PLAN_ID) or "").strip()
            if plan_id:
                entry["plan_ids"].add(plan_id)
            else:
                stats["rows_without_plan_id"] += 1

            for col in NAME_COLUMNS:
                value = (row.get(col) or "").strip()
                if value:
                    counts = entry["names"][col]
                    counts[value] = counts.get(value, 0) + 1

    return contracts, stats


def report_conflicts(contracts):
    """Print, on stderr, every contract whose name columns are not constant.

    Returns the number of (contract, column) pairs that disagreed.
    """
    conflicts = 0
    for contract_id in sorted(contracts):
        entry = contracts[contract_id]
        for col in NAME_COLUMNS:
            counts = entry["names"][col]
            if len(counts) > 1:
                conflicts += 1
                chosen = pick_value(counts)
                others = ", ".join(
                    f'"{v}" ({n} row{"s" if n != 1 else ""})'
                    for v, n in counts.items()
                    if v != chosen
                )
                print(
                    f'  WARNING [{contract_id}] {col}: using "{chosen}" '
                    f"({counts[chosen]} rows); also saw {others}",
                    file=sys.stderr,
                )
    return conflicts


def write_output(contracts, filepath):
    """Write one row per contract, sorted by contract number."""
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

    # QUOTE_ALL matches the quoting style of the CMS source file.
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow([OUT_COL_CONTRACT, OUT_COL_PLAN_COUNT, *NAME_COLUMNS])

        for contract_id in sorted(contracts):
            entry = contracts[contract_id]
            writer.writerow(
                [contract_id, len(entry["plan_ids"])]
                + [pick_value(entry["names"][col]) for col in NAME_COLUMNS]
            )


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Summarize a CMS Monthly Report By Plan CSV to one row per "
            "Medicare Advantage contract."
        )
    )
    parser.add_argument(
        "input_csv",
        metavar="INPUT_CSV",
        help="Plan level CMS Monthly Report By Plan CSV to read (required).",
    )
    parser.add_argument(
        "output_csv",
        metavar="OUTPUT_CSV",
        help="Contract level CSV to write (required); e.g. payer_by_ma_contract.csv",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    print("=" * 60)
    print("Medicare Advantage Contract Level Payer Extract")
    print("=" * 60)
    print()
    print(f"Reading plan level rows from:\n  {args.input_csv}")

    if not os.path.exists(args.input_csv):
        raise SystemExit(f"ERROR: input file not found: {args.input_csv}")

    contracts, stats = load_contracts(args.input_csv)
    conflicts = report_conflicts(contracts)
    write_output(contracts, args.output_csv)

    total_plan_ids = sum(len(e["plan_ids"]) for e in contracts.values())
    contracts_without_plans = sum(1 for e in contracts.values() if not e["plan_ids"])
    parent_orgs = {
        pick_value(e["names"][COL_PARENT_ORG])
        for e in contracts.values()
        if pick_value(e["names"][COL_PARENT_ORG])
    }

    print(f"\nWrote contract level summary to:\n  {args.output_csv}")
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Plan level rows read:                   {stats['rows']}")
    print(f"  Rows with no contract number:           {stats['skipped_no_contract']}")
    print(f"  Rows with an empty Plan ID:             {stats['rows_without_plan_id']}")
    print(f"  Unique contract numbers written:        {len(contracts)}")
    print(f"  Distinct plan IDs across contracts:     {total_plan_ids}")
    print(f"  Contracts with zero plan IDs:           {contracts_without_plans}")
    print(f"  Distinct parent organizations:          {len(parent_orgs)}")
    print(f"  Contract/column name inconsistencies:   {conflicts}")
    print()


if __name__ == "__main__":
    main()
