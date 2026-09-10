#!/usr/bin/env python3
"""Overlay HTE-format payer endpoint data onto the well-known payer index files.

Reads a CSV in the HTE PayerEndpoints release format
(https://github.com/ftrotter-gov/HTE_data_release_specifications/blob/main/data_release_specifications/PayerEndpoints.md)
together with a mapping.csv that documents how each source column, enumeration
approach, and endpoint type translates into the well-known index format, and
folds the endpoint data into the matching files under payer_index_files/.

Matching a source row to a payer
--------------------------------
1. By payer_lbn, normalized with FPI_maker_cli.normalize_legal_name and compared
   against the payerLegalName of each FPI identifier entry.  This is the primary
   path and the only one the spec guarantees, since payer_lbn is a required
   column.
2. Failing that, by (enumeration_approach, payer_id) looked up against the
   non-FPI identifier entries already present in the index.  This works only
   where the index already carries an identifier in that system.
3. Failing both, the row is reported and skipped.  A row with neither a legal
   name nor a payer id is skipped with a warning without further work.

Writing endpoints
-----------------
Endpoints are written into every plan_group of the matched payer file, because
the source data is payer-level unless plan_id says otherwise.  Three cases:

* key absent            -> the endpoint is added
* key present, same URL -> nothing happens (this is what makes re-runs idempotent)
* key present, new URL  -> the new value is added under "<key>#conflict_N" and
                           the file's top-level "has_conflict" is set to true

Sandbox URLs are written under a "_sandbox" suffixed key and are never
conflict-tracked: a sandbox value that disagrees with what is already recorded
prints a warning and is otherwise ignored.

Every file this tool touches is marked "is_seeded": false so that
tools/seed_medicare_advantage/seed.py will not overwrite the overlaid data on a
later seeding run.

Run from the repository root:
    python tools/overlay_HTE_release_format_payer_data/overlay.py \\
        --source raw_data_sources/1up_endpoints/1up_health.PayerEndpoints.csv \\
        --mapping raw_data_sources/1up_endpoints/mapping.csv

Add --dry-run to report what would change without writing anything.
"""

import argparse
import csv
import glob
import json
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
TOOLS_DIR = os.path.join(REPO_ROOT, "tools")
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)

from FPI_maker_cli import normalize_legal_name  # noqa: E402

PAYER_INDEX_DIR = os.path.join(REPO_ROOT, "payer_index_files")
SYSTEMS_FILE = os.path.join(REPO_ROOT, "reference_data",
                            "current_payer_identification_systems.json")
ENDPOINT_TYPES_FILE = os.path.join(REPO_ROOT, "reference_data", "endpoint_types.json")

# Marker appended to an endpoint key for a sandbox/testing URL.
SANDBOX_SUFFIX = "sandbox"
# Marker used when incoming data contradicts what is already recorded.
CONFLICT_SUFFIX = "conflict"


def load_mapping(*, path: str) -> dict:
    """Read mapping.csv and split it into the four kinds of mapping it carries.

    Returns a dict with:
      columns              -> source column name -> row dict
      enumeration_approach -> source value -> payer identifier system id
      endpoint_type        -> source value -> destination plan_endpoints key
      payer_override       -> normalized legal name -> row dict
    """
    mapping = {
        "columns": {},
        "enumeration_approach": {},
        "endpoint_type": {},
        "payer_override": {},
    }
    with open(path, encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            kind = (row.get("mapping_type") or "").strip()
            source_key = (row.get("source_key") or "").strip()
            destination_key = (row.get("destination_key") or "").strip()
            if not kind or not source_key:
                continue
            if kind == "column":
                mapping["columns"][source_key] = row
            elif kind == "enumeration_approach":
                mapping["enumeration_approach"][source_key] = destination_key
            elif kind == "endpoint_type":
                mapping["endpoint_type"][source_key] = destination_key
            elif kind == "payer_override":
                mapping["payer_override"][
                    normalize_legal_name(payer_legal_name=source_key)
                ] = row
    return mapping


def load_identifier_systems(*, path: str) -> dict:
    """Return a mapping of payer identifier system id -> system URL."""
    with open(path, encoding="utf-8") as handle:
        doc = json.load(handle)
    return {entry["id"]: entry["system"]
            for entry in doc.get("payer_identifier_systems", [])}


def load_known_endpoint_types(*, path: str) -> set:
    """Return the set of endpoint type names declared in the reference data."""
    with open(path, encoding="utf-8") as handle:
        return {entry["type"] for entry in json.load(handle)}


def iter_payer_files(*, base_dir: str):
    """Yield (filepath, document) for every readable well-known payer file."""
    pattern = os.path.join(base_dir, "*", "*", "*.well_known_payer.json")
    for filepath in sorted(glob.glob(pattern)):
        try:
            with open(filepath, encoding="utf-8") as handle:
                doc = json.load(handle)
        except (json.JSONDecodeError, OSError):
            continue
        # Redirect stubs ({"is_seeded": false, "new_file": ...}) carry no
        # identifiers and are not overlay targets.
        if "identifier" not in doc:
            continue
        yield filepath, doc


def build_payer_lookup(*, base_dir: str) -> tuple:
    """Build the two lookup tables used to match a source row to a payer file.

    Returns (by_legal_name, by_identifier) where
      by_legal_name : normalized legal name -> filepath
      by_identifier : (system_url, uppercased identifier value) -> filepath

    A value that resolves to more than one payer file is dropped from the
    identifier table, because an ambiguous match is worse than no match.
    """
    by_legal_name = {}
    by_identifier = {}
    ambiguous = set()

    for filepath, doc in iter_payer_files(base_dir=base_dir):
        for entry in doc["identifier"]:
            if entry.get("is_fpi"):
                legal_name = entry.get("payerLegalName")
                if legal_name:
                    key = normalize_legal_name(payer_legal_name=legal_name)
                    by_legal_name.setdefault(key, filepath)
            else:
                value = (entry.get("value") or "").strip().upper()
                if not value:
                    continue
                key = (entry.get("system"), value)
                if key in by_identifier and by_identifier[key] != filepath:
                    ambiguous.add(key)
                by_identifier.setdefault(key, filepath)

    for key in ambiguous:
        by_identifier.pop(key, None)

    return by_legal_name, by_identifier, ambiguous


def split_endpoint_key(*, key: str) -> tuple:
    """Split an endpoint key into (family, version).

    "carin_bluebutton_endpoint#1.0" -> ("carin_bluebutton_endpoint", "1.0")
    "payer_homepage"                -> ("payer_homepage", "")
    """
    if "#" in key:
        family, _, version = key.partition("#")
        return family, version
    return key, ""


def sandbox_key_for(*, key: str) -> str:
    """Return the sandbox variant of an endpoint key.

    A bare key gains "#sandbox"; a versioned key keeps its version and gains a
    "_sandbox" marker, e.g. "carin_bluebutton_endpoint#1.0" ->
    "carin_bluebutton_endpoint#1.0_sandbox".
    """
    family, version = split_endpoint_key(key=key)
    if version:
        return f"{family}#{version}_{SANDBOX_SUFFIX}"
    return f"{family}#{SANDBOX_SUFFIX}"


def conflict_key_for(*, key: str, existing_keys) -> str:
    """Return the next unused conflict variant of an endpoint key.

    A bare key becomes "<key>#conflict_1"; a versioned key becomes
    "<family>#<version>_conflict_1".  The counter increments until the key is
    unused, so repeated contradictory values accumulate rather than overwrite.
    """
    family, version = split_endpoint_key(key=key)
    index = 1
    while True:
        if version:
            candidate = f"{family}#{version}_{CONFLICT_SUFFIX}_{index}"
        else:
            candidate = f"{family}#{CONFLICT_SUFFIX}_{index}"
        if candidate not in existing_keys:
            return candidate
        index += 1


def find_matching_key(*, endpoints: dict, family: str) -> str:
    """Return an existing key in *endpoints* whose family matches, else "".

    The seeder writes versioned keys (davinci_pdex_provider_directory_endpoint#1.1)
    while the HTE source supplies bare ones.  Comparing on the family lets the
    overlay recognise that the two describe the same endpoint rather than
    silently creating a duplicate.  Sandbox and conflict variants are skipped:
    they are annotations on a primary value, not primary values themselves.
    """
    for existing in endpoints:
        existing_family, existing_version = split_endpoint_key(key=existing)
        if existing_family != family:
            continue
        if existing_version.endswith(f"_{SANDBOX_SUFFIX}") or existing_version == SANDBOX_SUFFIX:
            continue
        if re.search(rf"(^|_){CONFLICT_SUFFIX}_\d+$", existing_version):
            continue
        return existing
    return ""


def group_source_rows(*, path: str) -> list:
    """Read the HTE source file and group its rows into one bundle per payer.

    The HTE format is one row per endpoint, so several rows describe the same
    payer.  Rows are grouped by (payer_lbn, enumeration_approach, payer_id) so
    that each bundle becomes a single edit to a single payer file.

    Real-world files are inconsistent about repeating payer_lbn on every row of
    the same payer.  Before grouping, a legal name seen on any row of a given
    (enumeration_approach, payer_id) is backfilled onto the sibling rows that
    left it blank.  Without this, the blank-name rows would look like a separate
    unnamed payer, and would start matching by payer_id only after a previous
    run had added that identifier -- making the tool non-idempotent.
    """
    rows = []
    with open(path, encoding="utf-8", newline="") as handle:
        for line_number, row in enumerate(csv.DictReader(handle), start=2):
            clean = {key: (value or "").strip() for key, value in row.items()
                     if key is not None}
            rows.append((line_number, clean))

    known_names = {}
    for _, clean in rows:
        payer_id = clean.get("payer_id", "")
        legal_name = clean.get("payer_lbn", "")
        if payer_id and legal_name:
            known_names.setdefault(
                (clean.get("enumeration_approach", ""), payer_id), legal_name)

    bundles = {}
    for line_number, clean in rows:
        if not clean.get("payer_lbn"):
            inherited = known_names.get(
                (clean.get("enumeration_approach", ""), clean.get("payer_id", "")))
            if inherited:
                clean["payer_lbn"] = inherited
        group_key = (clean.get("payer_lbn", ""),
                     clean.get("enumeration_approach", ""),
                     clean.get("payer_id", ""))
        bundle = bundles.setdefault(group_key, {
            "payer_lbn": clean.get("payer_lbn", ""),
            "enumeration_approach": clean.get("enumeration_approach", ""),
            "payer_id": clean.get("payer_id", ""),
            "rows": [],
            "lines": [],
        })
        bundle["rows"].append(clean)
        bundle["lines"].append(line_number)
    return list(bundles.values())


def match_bundle(*, bundle, mapping, systems, by_legal_name, by_identifier):
    """Resolve a bundle to a payer file path.

    Returns (filepath, how) where *how* describes the match, or ("", reason)
    when no payer file could be resolved.
    """
    legal_name = bundle["payer_lbn"]
    payer_id = bundle["payer_id"]

    if not legal_name and not payer_id:
        return "", "no payer_lbn and no payer_id"

    if legal_name:
        key = normalize_legal_name(payer_legal_name=legal_name)
        override = mapping["payer_override"].get(key)
        if override is not None and override.get("transform") == "no_match":
            return "", f"payer_override: {override.get('notes', 'no match')}"
        filepath = by_legal_name.get(key)
        if filepath:
            return filepath, "payer_lbn"

    if payer_id:
        approach = bundle["enumeration_approach"]
        system_id = mapping["enumeration_approach"].get(approach)
        system_url = systems.get(system_id) if system_id else ""
        if system_url:
            filepath = by_identifier.get((system_url, payer_id.upper()))
            if filepath:
                return filepath, f"payer_id ({approach})"

    if legal_name:
        return "", "legal name not found in the payer index"
    return "", f"payer_id {bundle['enumeration_approach']}={payer_id} not found"


def add_crosswalk_identifier(*, doc, bundle, mapping, systems, report):
    """Add the row's (enumeration_approach, payer_id) as a crosswalk identifier.

    Written with is_fpi false and parent_fpi pointing at the file's first FPI,
    as required by WellKnownFileFormat.md.  Does nothing when the identifier is
    already present, which keeps re-runs idempotent.
    """
    approach = bundle["enumeration_approach"]
    value = bundle["payer_id"]
    if not approach or not value:
        return False

    system_id = mapping["enumeration_approach"].get(approach)
    if not system_id:
        report["unmapped_enumeration_approaches"].add(approach)
        return False

    system_url = systems.get(system_id)
    if not system_url:
        report["unknown_identifier_systems"].add(system_id)
        return False

    fpi_entries = [entry for entry in doc["identifier"] if entry.get("is_fpi")]
    if not fpi_entries:
        return False
    parent_fpi = fpi_entries[0]["value"]

    for entry in doc["identifier"]:
        if (entry.get("system") == system_url
                and (entry.get("value") or "").strip().upper() == value.upper()):
            return False

    doc["identifier"].append({
        "system": system_url,
        "value": value,
        "is_fpi": False,
        "parent_fpi": parent_fpi,
        "notes": f"Supplied by HTE PayerEndpoints release data ({approach}).",
    })
    report["identifiers_added"] += 1
    return True


def apply_endpoints(*, doc, bundle, mapping, known_types, report):
    """Write one bundle's endpoints into every plan_group of *doc*.

    Returns True when the document was modified.  Mutates *report* counters.
    """
    changed = False
    documentation_key = ""
    documentation_url = ""
    doc_mapping = mapping["columns"].get("documentation_url", {})
    if doc_mapping.get("transform") == "endpoint_url":
        documentation_key = doc_mapping.get("destination_key", "").strip()

    # Collect the endpoint writes this bundle asks for.
    writes = []           # (endpoint_key, url)
    sandbox_writes = []   # (endpoint_key, sandbox_url)
    for row in bundle["rows"]:
        source_type = row.get("fhir_url_type", "")
        url = row.get("fhir_url", "")
        if not source_type or not url:
            continue
        endpoint_key = mapping["endpoint_type"].get(source_type)
        if not endpoint_key:
            report["unmapped_endpoint_types"].add(source_type)
            continue
        family, _ = split_endpoint_key(key=endpoint_key)
        if family not in known_types:
            report["undeclared_endpoint_types"].add(family)
        writes.append((endpoint_key, url))
        sandbox_url = row.get("sandbox_fhir_url", "")
        if sandbox_url:
            sandbox_writes.append((endpoint_key, sandbox_url))
        if documentation_key and row.get("documentation_url"):
            documentation_url = row["documentation_url"]

    if documentation_key and documentation_url:
        writes.append((documentation_key, documentation_url))

    for group in doc.get("plan_groups", []):
        endpoints = group.setdefault("plan_endpoints", {})

        for endpoint_key, url in writes:
            family, _ = split_endpoint_key(key=endpoint_key)
            existing_key = find_matching_key(endpoints=endpoints, family=family)

            if not existing_key:
                endpoints[endpoint_key] = url
                changed = True
                report["endpoints_added"] += 1
                continue

            if endpoints[existing_key] == url:
                report["endpoints_unchanged"] += 1
                continue

            # Contradictory value: keep both, flag the file, never overwrite.
            already_recorded = any(
                value == url for key, value in endpoints.items()
                if split_endpoint_key(key=key)[0] == family
            )
            if already_recorded:
                report["endpoints_unchanged"] += 1
                continue

            new_key = conflict_key_for(key=existing_key, existing_keys=endpoints)
            endpoints[new_key] = url
            doc["has_conflict"] = True
            changed = True
            report["conflicts"].append(
                f"{bundle['payer_lbn'] or bundle['payer_id']}: {existing_key}="
                f"{endpoints[existing_key]} vs {new_key}={url}"
            )

        for endpoint_key, sandbox_url in sandbox_writes:
            key = sandbox_key_for(key=endpoint_key)
            if key not in endpoints:
                endpoints[key] = sandbox_url
                changed = True
                report["sandbox_added"] += 1
            elif endpoints[key] == sandbox_url:
                report["endpoints_unchanged"] += 1
            else:
                # Sandbox values are never conflict-tracked, by project decision.
                report["sandbox_conflicts"].append(
                    f"{bundle['payer_lbn'] or bundle['payer_id']}: {key} "
                    f"already={endpoints[key]} incoming={sandbox_url} (ignored)"
                )

    return changed


def new_report() -> dict:
    """Return an empty run report."""
    return {
        "matched_by_legal_name": 0,
        "matched_by_payer_id": 0,
        "unmatched": [],
        "skipped_blank": [],
        "files_changed": set(),
        "endpoints_added": 0,
        "endpoints_unchanged": 0,
        "sandbox_added": 0,
        "identifiers_added": 0,
        "conflicts": [],
        "sandbox_conflicts": [],
        "unmapped_endpoint_types": set(),
        "undeclared_endpoint_types": set(),
        "unmapped_enumeration_approaches": set(),
        "unknown_identifier_systems": set(),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Overlay HTE PayerEndpoints data onto the payer index files.")
    parser.add_argument("--source", required=True,
                        help="Path to the HTE-format PayerEndpoints CSV.")
    parser.add_argument("--mapping", required=True,
                        help="Path to the mapping.csv describing the translation.")
    parser.add_argument("--payer-index-dir", default=PAYER_INDEX_DIR,
                        help="Root of the payer index files (default: payer_index_files).")
    parser.add_argument("--dry-run", action="store_true",
                        help="Report what would change without writing anything.")
    args = parser.parse_args()

    print("=" * 68)
    print("HTE PayerEndpoints Overlay")
    print("=" * 68)
    print(f"Source : {args.source}")
    print(f"Mapping: {args.mapping}")
    print(f"Target : {args.payer_index_dir}")
    if args.dry_run:
        print("MODE   : dry run (no files will be written)")
    print()

    mapping = load_mapping(path=args.mapping)
    systems = load_identifier_systems(path=SYSTEMS_FILE)
    known_types = load_known_endpoint_types(path=ENDPOINT_TYPES_FILE)
    by_legal_name, by_identifier, ambiguous = build_payer_lookup(
        base_dir=args.payer_index_dir)

    print(f"Payer files indexed: {len(by_legal_name)} legal names, "
          f"{len(by_identifier)} crosswalk identifiers")
    if ambiguous:
        print(f"  ({len(ambiguous)} identifier value(s) ignored as ambiguous)")
    bundles = group_source_rows(path=args.source)
    print(f"Source payers (grouped rows): {len(bundles)}")
    print()

    report = new_report()
    # Documents are edited in memory and written once, so that several bundles
    # touching the same payer file accumulate rather than overwrite.
    loaded = {}

    for bundle in bundles:
        filepath, how = match_bundle(bundle=bundle, mapping=mapping, systems=systems,
                                     by_legal_name=by_legal_name,
                                     by_identifier=by_identifier)
        label = (bundle["payer_lbn"]
                 or f"{bundle['enumeration_approach']}={bundle['payer_id']}")
        if not filepath:
            if how == "no payer_lbn and no payer_id":
                report["skipped_blank"].append(
                    f"lines {bundle['lines'][0]}-{bundle['lines'][-1]}: {how}")
            else:
                report["unmatched"].append(f"{label or '(blank)'}: {how}")
            continue

        if how == "payer_lbn":
            report["matched_by_legal_name"] += 1
        else:
            report["matched_by_payer_id"] += 1

        if filepath not in loaded:
            with open(filepath, encoding="utf-8") as handle:
                loaded[filepath] = json.load(handle)
        doc = loaded[filepath]

        changed_id = add_crosswalk_identifier(doc=doc, bundle=bundle, mapping=mapping,
                                              systems=systems, report=report)
        changed_ep = apply_endpoints(doc=doc, bundle=bundle, mapping=mapping,
                                     known_types=known_types, report=report)
        if changed_id or changed_ep:
            report["files_changed"].add(filepath)

    # Persist.  Every touched file is marked not-seeded so the Medicare Advantage
    # seeder leaves the overlaid data alone on its next run.
    for filepath in sorted(report["files_changed"]):
        doc = loaded[filepath]
        doc["is_seeded"] = False
        doc.setdefault("has_conflict", False)
        if not args.dry_run:
            with open(filepath, "w", encoding="utf-8") as handle:
                json.dump(doc, handle, indent=2)
                handle.write("\n")

    print_report(report=report, dry_run=args.dry_run)


def print_report(*, report, dry_run):
    """Print the end-of-run summary."""
    print("-" * 68)
    print("RESULTS")
    print("-" * 68)
    print(f"  Matched by payer_lbn:        {report['matched_by_legal_name']}")
    print(f"  Matched by payer_id:         {report['matched_by_payer_id']}")
    print(f"  Unmatched:                   {len(report['unmatched'])}")
    print(f"  Skipped (no name and no id): {len(report['skipped_blank'])}")
    print()
    print(f"  Files changed:               {len(report['files_changed'])}")
    print(f"  Endpoints added:             {report['endpoints_added']}")
    print(f"  Sandbox endpoints added:     {report['sandbox_added']}")
    print(f"  Crosswalk identifiers added: {report['identifiers_added']}")
    print(f"  Already present (no change): {report['endpoints_unchanged']}")
    print(f"  Conflicts recorded:          {len(report['conflicts'])}")
    print()

    if report["conflicts"]:
        print("  CONFLICTS (both values kept; has_conflict set to true):")
        for line in report["conflicts"]:
            print(f"    ! {line}")
        print()

    if report["sandbox_conflicts"]:
        print("  SANDBOX CONFLICTS (warned and ignored, by design):")
        for line in report["sandbox_conflicts"]:
            print(f"    ~ {line}")
        print()

    if report["unmatched"]:
        print("  UNMATCHED SOURCE PAYERS:")
        for line in report["unmatched"]:
            print(f"    - {line}")
        print()

    if report["skipped_blank"]:
        print("  SKIPPED ROWS (no payer_lbn and no payer_id):")
        for line in report["skipped_blank"]:
            print(f"    - {line}")
        print()

    for key, title in (
        ("unmapped_endpoint_types", "Endpoint types missing from mapping.csv"),
        ("undeclared_endpoint_types", "Endpoint types missing from endpoint_types.json"),
        ("unmapped_enumeration_approaches", "Enumeration approaches missing from mapping.csv"),
        ("unknown_identifier_systems", "Identifier systems missing from reference data"),
    ):
        if report[key]:
            print(f"  {title}: {sorted(report[key])}")

    if dry_run:
        print("  (dry run: nothing was written)")


if __name__ == "__main__":
    main()
