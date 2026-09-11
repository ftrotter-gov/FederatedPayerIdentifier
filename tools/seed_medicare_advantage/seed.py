#!/usr/bin/env python3
"""Reads two CMS Medicare Advantage CSV files and generates one well-known payer JSON file per unique payer name.

Previous approach: one file per contract_id, FPI derived from contract_id.
                   (That was a mistake in reasoning: contract IDs identify
                   contracts, not payer legal entities, and must never be used
                   as an FPI source by this seed.)
Current approach:  one file per unique *normalized payer name*, FPI derived
                   from the LEGAL_NAME_HASH identifier system.

Plan and payer census
---------------------
The CMS "Monthly Report By Plan" public use file
(Monthly_Report_By_Plan_2026_08.puf.csv) is the primary source.  It replaces the
plan crosswalk file the seed previously consumed.  Every contract in the monthly
report gets seeded, regardless of its Organization Type: Local and Regional CCP,
PDP, National PACE, 1876 Cost, HCPP, PFFS, MSA and LI NET contracts are all
included.

The monthly report supplies, per contract, all of the following:

* Organization Name            - the payer legal name, and therefore the
                                 LEGAL_NAME_HASH source for the FPI
* Organization Marketing Name  - a payer-level search alias
* Parent Organization          - a payer-level search alias
* Plan ID / Plan Name          - the plan roster

The three name columns are properties of the contract rather than of the
individual plan, and are constant within a contract in the source data.  All
three are published together in the FPI identifier's
"payer_level_string_search_matches" list, so that a payer can be matched from
its legal name, its marketing brand, or its corporate parent.

Endpoint coverage
-----------------
Two separate URL files contribute endpoints.  A contract may receive an entry
from either, both, or neither; all endpoints known for a contract land in the
same "plan_endpoints" object.

payer_fhir_api_url.csv holds queryable FHIR Plan-Net API base URLs:

* any usable URL -> davinci_pdex_provider_directory_endpoint#1.1

payer_url_list.csv holds Medicare Plan Finder provider directory files, and its
"Response Format" column selects the key:

* "FHIR JSON"             -> davinci_pdex_provider_directory_endpoint_all_at_once#1.1
                             (a bulk pre-generated directory download, not a
                             queryable API)
* "Machine-readable JSON" -> cms_provider_directory_machine_readable_format_endpoint
                             (the non-FHIR CMS provider directory index file;
                             see reference_data/endpoint_types.json)

A contract whose URL cell is empty, or that lists several space-separated URLs
(no multi-URL strategy is defined yet), still produces a seed file.  Its
plan_group simply carries an empty "plan_endpoints" object, which per
WellKnownFileFormat.md means the index makes no assertion about that payer's
endpoints yet.  These "empty" seed files exist so that the FPI, the contract
IDs, and the plan roster are published and curatable now, with endpoints filled
in later.

A handful of contracts appear in the URL files but no longer appear in the
monthly report (their contracts have ended).  They are still seeded, using the
legal name carried in the URL file, with an empty plan roster.  Where both
sources name a contract, the monthly report's Organization Name wins and the
disagreement is reported.

The legal name is the only payer attribute reliably available to CMS at seed
time, so the seed hashes it — a temporary hack until payers publish FPIs
derived from real identifier systems (NAIC_ID, HIOS_ID, LEI, etc.).

All uuid generation and legal-name normalization logic lives in
tools/FPI_maker_cli.py (the single home of FPI hashing in this repository).
The normalization rule applied there: lowercase the raw payer name, then strip
every character that is not a-z or 0-9 (e.g. "AETNA HEALTH, INC." becomes
"aetnahealthinc").  Multiple contract IDs that produce the same normalized
name are treated as the same payer entity and are consolidated into a single
well-known JSON file.  Plans from different contracts that point to different
FHIR endpoints are placed in separate plan_groups within that one file.
"""

import csv
import json
import os
import re
import sys
import uuid

# Locate the source data and output directories relative to this script's location.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))

PAYER_URL_FILE = os.path.join(SCRIPT_DIR, "source_data", "payer_url_list.csv")
FHIR_API_URL_FILE = os.path.join(SCRIPT_DIR, "source_data", "payer_fhir_api_url.csv")
MONTHLY_REPORT_FILE = os.path.join(
    SCRIPT_DIR, "source_data", "Monthly_Report_By_Plan_2026_08.puf.csv"
)
OUTPUT_BASE_DIR = os.path.join(REPO_ROOT, "payer_index_files", "medicare_advantage")

# The CMS monthly report is exported from a Windows toolchain and is not valid
# UTF-8: some plan names contain cp1252 punctuation (e.g. 0x96, an en dash).
# Try UTF-8 first (with BOM tolerance) and fall back to cp1252, which decodes
# every byte value and so cannot fail.  Mirrors extract_payers.py.
SOURCE_ENCODINGS = ("utf-8-sig", "cp1252")

# Column names as they appear in the first line of the monthly report CSV.
COL_CONTRACT = "Contract Number"
COL_PLAN_ID = "Plan ID"
COL_PLAN_NAME = "Plan Name"
COL_ORG_TYPE = "Organization Type"
COL_ORG_NAME = "Organization Name"
COL_ORG_MARKETING_NAME = "Organization Marketing Name"
COL_PARENT_ORG = "Parent Organization"

# Import the shared FPI generation library from the tools directory.
TOOLS_DIR = os.path.join(REPO_ROOT, "tools")
if TOOLS_DIR not in sys.path:
    sys.path.insert(0, TOOLS_DIR)
from FPI_maker_cli import generate_fpi, normalize_legal_name  # noqa: E402

# System URI strings used in the identifier and plan_identifiers blocks.
# These correspond to entries in reference_data/current_payer_identification_systems.json.
# FPI: the Federated Payer Identifier generated by this project.
SYSTEM_FPI = "https://directory.cms.gov/payer_identification_system/fpi"
# CMS_CONTRACT_ID: the Medicare Advantage contract ID that most of the source data is coded in.
SYSTEM_CMS_CONTRACT_ID = "https://directory.cms.gov/payer_identification_system/cms_contract_id"
# LEGAL_NAME_HASH: the identifier system used by this seed to generate the FPI
# (a UUID5 derived from the normalized payer legal name).  Recorded on the FPI
# identifier entry as "fpi_source_system".
SYSTEM_LEGAL_NAME_HASH = "https://directory.cms.gov/payer_identification_system/legal_name_hash"
# Medicare plan identifier: the CMS contract ID plus plan segment (e.g. "H3146-001").
SYSTEM_MEDICARE_PLAN = "https://directory.cms.gov/payer_identification_system/cms_contract_id/plan/plan_id"
RESOURCE_TYPE = "http://hl7.org/fhir/us/fast-ndh/StructureDefinition/NDHPayerWellknownDefinition"

# Endpoint keys extractable from these data sources.
#
# payer_fhir_api_url.csv lists queryable Da Vinci PDex Plan-Net provider
# directory API base URLs — a live FHIR server that answers one resource query
# at a time.
ENDPOINT_KEY = "davinci_pdex_provider_directory_endpoint#1.1"
# payer_url_list.csv "FHIR JSON" rows point at a pre-generated bulk download of
# the payer's complete provider directory, not at a queryable API, so they take
# the all-at-once key.  See reference_data/endpoint_types.json.
ALL_AT_ONCE_ENDPOINT_KEY = "davinci_pdex_provider_directory_endpoint_all_at_once#1.1"
# payer_url_list.csv "Machine-readable JSON" rows point at the non-FHIR CMS
# provider directory index file (the format first used for healthcare.gov, later
# adopted for Medicare Advantage).  It carries no IG version, so like
# "payer_homepage" the key has no "#version" suffix.
MACHINE_READABLE_ENDPOINT_KEY = "cms_provider_directory_machine_readable_format_endpoint"

# System ID used as the FPI namespace when deriving identifiers from payer names.
# LEGAL_NAME_HASH is the hashing system defined in
# reference_data/current_payer_identification_systems.json; FPI_maker_cli
# normalizes the legal name automatically before hashing under this system.
FPI_SYSTEM_ID = "LEGAL_NAME_HASH"


def safe_name(name):
    """Convert a payer name to a lowercase, underscore-separated, special-character-free directory name."""
    name = name.lower().replace(" ", "_")
    name = re.sub(r"[^a-z0-9_]", "", name)
    name = re.sub(r"_+", "_", name).strip("_")
    return name


def parse_contract_id_field(field_value):
    """Split the combined 'H0028 - PAYER NAME' field into separate contract_id and payer_name strings."""
    parts = field_value.split(" - ", 1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return None, None


def open_source_csv(filepath):
    """Open a source CSV, trying each supported encoding in turn.

    Returns the open file object.  newline="" lets the csv module handle the
    file's CRLF line endings itself.  The CMS monthly report is not valid UTF-8,
    so cp1252 is used as the fallback; it decodes every byte value and so cannot
    fail.  Mirrors the helper of the same name in extract_payers.py.
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


def load_fhir_api_urls(filepath):
    """Read payer_fhir_api_url.csv and return (urls, stats).

    urls maps contract_id -> {"payer_name": str, "url": str}.  Every row that
    yields a contract ID and a payer name is kept even when the URL is unusable,
    because the payer name is a fallback legal-name source for contracts that no
    longer appear in the monthly report.

    All URLs in this file are queryable FHIR Plan-Net API base URLs, so they all
    take ENDPOINT_KEY.  Cells holding several space-separated URLs are not usable
    (plan_endpoints values are single strings and no multi-URL strategy is
    defined yet), so their URL is cleared but the row is still kept.
    """
    urls = {}
    stats = {"total": 0, "no_url": 0, "multi_url": 0,
             "skipped_no_contract_id": 0, "with_url": 0}

    with open_source_csv(filepath) as f:
        for row in csv.DictReader(f):
            stats["total"] += 1

            contract_id, payer_name = parse_contract_id_field(
                row.get("Contract ID", "").strip()
            )
            if not contract_id or not payer_name:
                stats["skipped_no_contract_id"] += 1
                continue

            url = (row.get("FHIR Provider Directory API URL") or "").strip()
            if not url:
                stats["no_url"] += 1
                url = ""
            elif len(url.split()) > 1:
                # Several URLs in one cell (typically one per FHIR resource type).
                stats["multi_url"] += 1
                url = ""
            else:
                stats["with_url"] += 1

            urls[contract_id] = {"payer_name": payer_name, "url": url}

    return urls, stats


def load_mpf_urls(filepath):
    """Read payer_url_list.csv and return (urls, stats).

    urls maps contract_id -> {"payer_name": str, "url": str, "endpoint_key": str}.
    The "Response Format" column selects the endpoint key: "FHIR JSON" rows are
    bulk directory downloads (ALL_AT_ONCE_ENDPOINT_KEY) while
    "Machine-readable JSON" rows are the non-FHIR CMS index file
    (MACHINE_READABLE_ENDPOINT_KEY).

    As with the FHIR API file, rows are kept even when the URL is unusable so
    that the payer name remains available as a fallback legal-name source.
    """
    urls = {}
    stats = {"total": 0, "no_url": 0, "multi_url": 0, "unknown_format": 0,
             "skipped_no_contract_id": 0, "all_at_once": 0, "machine_readable": 0}

    with open_source_csv(filepath) as f:
        for row in csv.DictReader(f):
            stats["total"] += 1

            contract_id, payer_name = parse_contract_id_field(
                row.get("Contract ID", "").strip()
            )
            if not contract_id or not payer_name:
                stats["skipped_no_contract_id"] += 1
                continue

            url = (row.get("MPF Provider Directory URL") or "").strip()
            response_format = (row.get("Response Format") or "").strip().lower()

            endpoint_key = ""
            if not url:
                stats["no_url"] += 1
                url = ""
            elif len(url.split()) > 1:
                stats["multi_url"] += 1
                url = ""
            elif response_format == "machine-readable json":
                endpoint_key = MACHINE_READABLE_ENDPOINT_KEY
                stats["machine_readable"] += 1
            elif response_format == "fhir json":
                endpoint_key = ALL_AT_ONCE_ENDPOINT_KEY
                stats["all_at_once"] += 1
            else:
                # An unrecognised response format cannot be mapped to a key, so
                # the URL is not published.  Reported rather than guessed at.
                stats["unknown_format"] += 1
                url = ""

            urls[contract_id] = {
                "payer_name": payer_name,
                "url": url,
                "endpoint_key": endpoint_key,
            }

    return urls, stats


def load_monthly_report(filepath):
    """Read the CMS Monthly Report By Plan CSV and return (contracts, stats).

    contracts maps contract_id -> {
        "org_name":       str,   # Organization Name (the payer legal name)
        "marketing_name": str,   # Organization Marketing Name
        "parent_org":     str,   # Parent Organization
        "org_type":       str,   # Organization Type (reported, not published)
        "plans":          [{"plan_id": str, "plan_name": str}],
    }

    The monthly report is a plan level file: one row per contract/plan-id pair.
    The four contract level columns are constant within a contract in the source
    data, so the first non-empty value seen for a contract is taken and later
    rows only contribute plans.  Any disagreement is recorded in
    stats["name_conflicts"] so it stays visible rather than being silently
    flattened.

    Rows with an empty Plan ID are cost/HCPP style contracts that have no plan
    segment.  They establish the contract and its names but contribute no plan,
    so such a contract legitimately ends up with an empty plan list rather than
    a malformed "CONTRACT-" plan identifier.
    """
    contracts = {}
    seen_plans = set()  # (contract_id, plan_id) guards against duplicate rows.
    stats = {"rows": 0, "skipped_no_contract": 0, "rows_without_plan_id": 0,
             "name_conflicts": []}

    with open_source_csv(filepath) as f:
        for row in csv.DictReader(f):
            stats["rows"] += 1

            contract_id = (row.get(COL_CONTRACT) or "").strip()
            if not contract_id:
                stats["skipped_no_contract"] += 1
                continue

            org_name = (row.get(COL_ORG_NAME) or "").strip()
            marketing_name = (row.get(COL_ORG_MARKETING_NAME) or "").strip()
            parent_org = (row.get(COL_PARENT_ORG) or "").strip()
            org_type = (row.get(COL_ORG_TYPE) or "").strip()

            entry = contracts.get(contract_id)
            if entry is None:
                entry = contracts[contract_id] = {
                    "org_name": org_name,
                    "marketing_name": marketing_name,
                    "parent_org": parent_org,
                    "org_type": org_type,
                    "plans": [],
                }
            else:
                # Contract level columns should not vary within a contract.
                for column, established, found in (
                    (COL_ORG_NAME, entry["org_name"], org_name),
                    (COL_ORG_MARKETING_NAME, entry["marketing_name"], marketing_name),
                    (COL_PARENT_ORG, entry["parent_org"], parent_org),
                ):
                    if found and established and found != established:
                        stats["name_conflicts"].append(
                            (contract_id, column, established, found)
                        )
                # Fill in any column that was blank on the contract's first row.
                entry["org_name"] = entry["org_name"] or org_name
                entry["marketing_name"] = entry["marketing_name"] or marketing_name
                entry["parent_org"] = entry["parent_org"] or parent_org
                entry["org_type"] = entry["org_type"] or org_type

            plan_id = (row.get(COL_PLAN_ID) or "").strip()
            if not plan_id:
                # No plan segment: the contract exists but carries no plan here.
                stats["rows_without_plan_id"] += 1
                continue

            if (contract_id, plan_id) in seen_plans:
                continue
            seen_plans.add((contract_id, plan_id))

            entry["plans"].append({
                "plan_id": plan_id,
                "plan_name": (row.get(COL_PLAN_NAME) or "").strip(),
            })

    return contracts, stats


def build_contract_registry(monthly, fhir_urls, mpf_urls):
    """Merge the three sources into one per-contract registry.

    Returns (registry, stats).  registry maps contract_id -> {
        "legal_name":     str,        # FPI / payerLegalName source
        "search_matches": [str],      # payer-level aliases, order preserved
        "org_type":       str,
        "plans":          [{"plan_id", "plan_name"}],
        "endpoints":      {key: url}, # every endpoint known for this contract
    }

    The monthly report is authoritative for the legal name.  Contracts that
    appear only in a URL file fall back to the legal name carried there, so an
    ended contract that still has a published endpoint is not silently dropped.
    """
    stats = {"name_disagreements": [], "url_only_contracts": [],
             "monthly_only_contracts": 0, "no_legal_name": []}

    registry = {}

    for contract_id in sorted(set(monthly) | set(fhir_urls) | set(mpf_urls)):
        monthly_entry = monthly.get(contract_id)

        # --- legal name and payer-level search aliases ---
        if monthly_entry and monthly_entry["org_name"]:
            legal_name = monthly_entry["org_name"]
            # Organization Name, marketing name and parent organization are all
            # published as payer-level search strings.  Deduplicate them
            # case-insensitively while preserving first-seen order.
            search_matches = []
            seen_matches = set()
            for alias in (monthly_entry["org_name"],
                          monthly_entry["marketing_name"],
                          monthly_entry["parent_org"]):
                if alias and alias.lower() not in seen_matches:
                    search_matches.append(alias)
                    seen_matches.add(alias.lower())
            # Where both sources name a contract the monthly report wins; the
            # disagreement is reported rather than silently resolved.
            for source in (fhir_urls, mpf_urls):
                url_name = (source.get(contract_id) or {}).get("payer_name", "")
                if url_name and normalize_legal_name(payer_legal_name=url_name) != \
                        normalize_legal_name(payer_legal_name=legal_name):
                    stats["name_disagreements"].append(
                        (contract_id, legal_name, url_name)
                    )
                    break
        else:
            # Contract absent from the monthly report (typically ended): fall
            # back to the legal name in whichever URL file carries it.
            legal_name = ((fhir_urls.get(contract_id) or {}).get("payer_name")
                          or (mpf_urls.get(contract_id) or {}).get("payer_name")
                          or "")
            search_matches = [legal_name] if legal_name else []
            stats["url_only_contracts"].append(contract_id)

        if not legal_name:
            # Nothing to hash into an FPI, and a contract ID must never be used
            # as an FPI source.  Cannot occur with the current sources, but the
            # guard keeps the invariant explicit.
            stats["no_legal_name"].append(contract_id)
            continue

        if monthly_entry and contract_id not in fhir_urls and contract_id not in mpf_urls:
            stats["monthly_only_contracts"] += 1

        # --- endpoints: one contract may contribute several keys at once ---
        endpoints = {}
        fhir_entry = fhir_urls.get(contract_id)
        if fhir_entry and fhir_entry["url"]:
            endpoints[ENDPOINT_KEY] = fhir_entry["url"]
        mpf_entry = mpf_urls.get(contract_id)
        if mpf_entry and mpf_entry["url"] and mpf_entry["endpoint_key"]:
            endpoints[mpf_entry["endpoint_key"]] = mpf_entry["url"]

        registry[contract_id] = {
            "legal_name": legal_name,
            "search_matches": search_matches,
            "org_type": (monthly_entry or {}).get("org_type", ""),
            "plans": (monthly_entry or {}).get("plans", []),
            "endpoints": endpoints,
        }

    return registry, stats


def group_payers_by_name(registry):
    """
    Re-group the per-contract registry into a dict keyed by normalized payer name.

    Contracts whose legal names normalize to the same string are the same payer
    legal entity and are consolidated into a single well-known file under one
    FPI.  Their payer-level search strings are unioned, so a merged payer is
    matchable by every marketing brand and corporate parent its contracts carry.

    Returns
    -------
    dict[str, dict]
        Mapping of normalized_name ->
            {
                "canonical_name": str,          # first raw name seen (sorted by contract_id)
                "search_matches": [str],        # union across the group's contracts
                "contracts": [                  # all contracts sharing this normalized name
                    {"contract_id": str, "endpoints": dict, "plans": list,
                     "org_type": str},
                    ...
                ]
            }
    """
    groups = {}
    for contract_id in sorted(registry.keys()):
        info = registry[contract_id]
        norm = normalize_legal_name(payer_legal_name=info["legal_name"])

        group = groups.get(norm)
        if group is None:
            group = groups[norm] = {
                "canonical_name": info["legal_name"],
                "search_matches": [],
                "contracts": [],
            }

        # Union the aliases, still case-insensitively deduplicated.
        existing = {alias.lower() for alias in group["search_matches"]}
        for alias in info["search_matches"]:
            if alias.lower() not in existing:
                group["search_matches"].append(alias)
                existing.add(alias.lower())

        group["contracts"].append({
            "contract_id": contract_id,
            "endpoints": info["endpoints"],
            "plans": info["plans"],
            "org_type": info["org_type"],
        })

    return groups


def build_well_known_json(normalized_name, canonical_name, contract_entries,
                          search_matches=None, existing_f_plan_ids=None):
    """
    Construct the well-known payer JSON document for one logical payer.

    The FPI is derived from the normalized payer name.  All contracts that share
    the same normalized name are included as additional identifiers.  Plans whose
    contracts expose different sets of endpoints are placed in separate
    plan_groups so that endpoint routing remains unambiguous.

    Parameters
    ----------
    normalized_name : str
        The all-lowercase, special-character-free payer name key (used for FPI).
    canonical_name : str
        The human-readable payer name to store in payerLegalName.
    contract_entries : list[dict]
        Each entry has "contract_id", "endpoints" (a {key: url} dict) and
        "plans" (a list of {plan_id, plan_name} dicts).
    search_matches : list[str] | None
        Payer-level search strings (organization, marketing and parent
        organization names) published inside the FPI identifier entry.
    existing_f_plan_ids : dict[str, str] | None
        Maps an already-published plan identifier value (e.g. "H3146-001") to the
        f_plan_id previously assigned to it, so that value is preserved instead
        of being randomly regenerated.

    Returns
    -------
    tuple[dict, str, int]
        (well-known JSON document, fpi string, total plan count)
    """
    # FPI_maker_cli normalizes the legal name internally for LEGAL_NAME_HASH,
    # so passing the raw canonical name here yields the same FPI as passing
    # the pre-normalized name.  That means the recorded "fpi_source_value"
    # below (the raw legal name) genuinely reproduces the FPI.
    fpi = generate_fpi(system_id=FPI_SYSTEM_ID, payer_id_value=canonical_name)
    existing_f_plan_ids = existing_f_plan_ids or {}

    # Build the identifier block.
    #
    # New multi-FPI format (WellKnownFileFormat.md, merged in PR #1):
    #   - Every identifier entry MUST include "is_fpi" (Boolean).
    #   - The FPI entry has is_fpi: true and carries payerLegalName inside it.
    #     payerLegalName is NO LONGER a top-level field.
    #   - Every non-FPI identifier has is_fpi: false and MUST carry parent_fpi
    #     (the UUID of the owning FPI in this same file).
    #   - Every plan identifier MUST carry parent_fpi and a random f_plan_id.
    fpi_entry = {
        "system": SYSTEM_FPI,
        "value": fpi,
        "is_fpi": True,
        "payerLegalName": canonical_name,
    }
    # payer_level_string_search_matches is scoped to this FPI's legal entity and
    # MUST live inside the FPI identifier entry, never at the file root
    # (WellKnownFileFormat.md validation rule 7).  The strings come from the
    # monthly report's organization, marketing and parent organization names.
    if search_matches:
        fpi_entry["payer_level_string_search_matches"] = list(search_matches)
    fpi_entry["fpi_source_system"] = SYSTEM_LEGAL_NAME_HASH
    fpi_entry["fpi_source_value"] = canonical_name
    identifier = [fpi_entry]
    for entry in contract_entries:
        identifier.append({
            "system": SYSTEM_CMS_CONTRACT_ID,
            "value": entry["contract_id"],
            "is_fpi": False,
            "parent_fpi": fpi,
        })

    # Group plans by their contract's complete set of endpoints.  Per
    # WellKnownFileFormat.md a plan_group is defined by having exactly the same
    # set of endpoint links, so the bucket identity is the whole {key: url}
    # mapping — not a single endpoint.  One contract may now carry a queryable
    # FHIR directory, a bulk all-at-once download and a CMS machine-readable
    # index simultaneously, and all three belong in the same plan_group.  The
    # empty bucket is the "endpoint unknown" case: those plans are still
    # published, in a plan_group that asserts no endpoint.
    endpoint_to_plans = {}   # frozenset of (key, url) -> list of plans
    for entry in contract_entries:
        contract_id = entry["contract_id"]
        endpoints = entry.get("endpoints") or {}
        bucket = frozenset(endpoints.items())
        if bucket not in endpoint_to_plans:
            endpoint_to_plans[bucket] = []
        # Deduplicate plans within the same endpoint bucket.
        seen_plan_keys = {(p["contract_plan_id"], p["plan_name"])
                          for p in endpoint_to_plans[bucket]}
        for plan in entry.get("plans", []):
            # Contracts with no plan segment contribute no plan identifier; a
            # blank plan id must never produce a "CONTRACT-" style value.
            if not plan["plan_id"]:
                continue
            # The full Medicare plan identifier is the contract number plus the
            # plan segment, joined by a hyphen (e.g. "H3146-001").
            contract_plan_id = f"{contract_id}-{plan['plan_id']}"
            key = (contract_plan_id, plan["plan_name"])
            if key not in seen_plan_keys:
                endpoint_to_plans[bucket].append({
                    "contract_plan_id": contract_plan_id,
                    "plan_name": plan["plan_name"],
                })
                seen_plan_keys.add(key)

    plan_groups = []
    total_plans = 0
    # Sort by the bucket's sorted key/url pairs so that repeated runs emit
    # plan_groups in a stable order.
    for bucket in sorted(endpoint_to_plans, key=lambda b: sorted(b)):
        plans = endpoint_to_plans[bucket]
        plan_identifiers = []
        for plan in plans:
            entry = {
                "system": SYSTEM_MEDICARE_PLAN,
                "value": plan["contract_plan_id"],
                # parent_fpi links this plan to the owning FPI (validation rule 5 & 6).
                "parent_fpi": fpi,
                # f_plan_id is a UUIDv4 unique to this plan entry.  It is minted
                # once and then reused on later runs (see load_existing_f_plan_ids)
                # so that re-seeding does not churn every published plan entry.
                "f_plan_id": existing_f_plan_ids.get(
                    plan["contract_plan_id"], str(uuid.uuid4())
                ),
            }
            if plan["plan_name"]:
                entry["plan_name"] = plan["plan_name"]
            plan_identifiers.append(entry)
        # An empty bucket means no endpoint is known for these plans.  Per
        # WellKnownFileFormat.md, omitting an endpoint key means the index makes
        # no assertion for that protocol, so absent keys are left out entirely
        # rather than written as null or as an empty string.  Keys are emitted in
        # sorted order for stable output.
        plan_endpoints = {key: url for key, url in sorted(bucket)}
        plan_groups.append({
            "plan_identifiers": plan_identifiers,
            "plan_endpoints": plan_endpoints,
        })
        total_plans += len(plan_identifiers)

    # payerLegalName is now inside the FPI identifier entry, NOT at the top level.
    doc = {
        "copied_from_url": None,
        "resourceType": RESOURCE_TYPE,
        "identifier": identifier,
        "plan_groups": plan_groups,
        "is_seeded": True,
    }

    return doc, fpi, total_plans


# The complete set of top-level keys the seed writes.
# NOTE: "payerLegalName" is no longer a top-level key; it lives inside the FPI identifier entry.
SEED_TOP_LEVEL_KEYS = {"copied_from_url", "is_seeded", "resourceType", "identifier", "plan_groups"}

# Keys the seed writes inside each plan_identifier entry.
# parent_fpi and f_plan_id are new required fields from the multi-FPI format (PR #1).
SEED_PLAN_IDENTIFIER_KEYS = {"system", "value", "plan_name", "parent_fpi", "f_plan_id"}

# Keys the seed writes inside each plan_group entry.
SEED_PLAN_GROUP_KEYS = {"plan_identifiers", "plan_endpoints"}

# Keys the seed writes inside each identifier entry.
# is_fpi is required on every identifier entry (multi-FPI format).
# parent_fpi is required on non-FPI entries (is_fpi: false).
# payerLegalName, payer_level_string_search_matches, fpi_source_system and
# fpi_source_value appear only on the FPI entry (is_fpi: true).
SEED_IDENTIFIER_KEYS = {"system", "value", "is_fpi", "parent_fpi", "payerLegalName",
                        "payer_level_string_search_matches",
                        "fpi_source_system", "fpi_source_value"}

# Endpoint keys the seed ever writes.  A plan_group may carry several at once.
SEED_ENDPOINT_KEYS = {ENDPOINT_KEY, ALL_AT_ONCE_ENDPOINT_KEY,
                      MACHINE_READABLE_ENDPOINT_KEY}


def collect_extra_fields(existing_doc, seed_doc):
    """Return a list of human-readable descriptions of any fields present in existing_doc
    that go beyond what the seed would produce (seed_doc is used only to identify the
    seed-generated endpoint key for that contract)."""
    extras = []

    # --- Top-level keys ---
    for key in existing_doc:
        if key not in SEED_TOP_LEVEL_KEYS:
            extras.append(f"top-level key '{key}'")

    # --- identifier entries ---
    for i, id_entry in enumerate(existing_doc.get("identifier", [])):
        for key in id_entry:
            if key not in SEED_IDENTIFIER_KEYS:
                extras.append(f"identifier[{i}] key '{key}'")

    # --- plan_groups ---
    for gi, group in enumerate(existing_doc.get("plan_groups", [])):
        for key in group:
            if key not in SEED_PLAN_GROUP_KEYS:
                extras.append(f"plan_groups[{gi}] key '{key}'")

        # plan_identifiers entries
        for pi, plan_id_entry in enumerate(group.get("plan_identifiers", [])):
            for key in plan_id_entry:
                if key not in SEED_PLAN_IDENTIFIER_KEYS:
                    extras.append(f"plan_groups[{gi}].plan_identifiers[{pi}] key '{key}'")

        # plan_endpoints keys
        for ep_key in group.get("plan_endpoints", {}):
            if ep_key not in SEED_ENDPOINT_KEYS:
                extras.append(f"plan_groups[{gi}].plan_endpoints key '{ep_key}'")

    return extras


def load_existing_f_plan_ids(*, output_dir: str) -> dict:
    """Return a mapping of plan identifier value -> f_plan_id already on disk for this payer.

    f_plan_id is a random UUIDv4 with no derivable source, so regenerating it on
    every run would rewrite every plan entry in every file and bury real changes
    in churn.  Downstream consumers may also have stored these values.  The seed
    therefore reuses any f_plan_id it has already published for a given plan and
    mints a new one only for plans it has not seen before.
    """
    existing = {}
    if not os.path.isdir(output_dir):
        return existing
    for existing_name in sorted(os.listdir(output_dir)):
        if not existing_name.endswith(".well_known_payer.json"):
            continue
        try:
            with open(os.path.join(output_dir, existing_name), encoding="utf-8") as existing_file:
                existing_doc = json.load(existing_file)
        except (json.JSONDecodeError, OSError):
            continue
        for group in existing_doc.get("plan_groups", []):
            for plan_entry in group.get("plan_identifiers", []):
                value = plan_entry.get("value")
                f_plan_id = plan_entry.get("f_plan_id")
                if value and f_plan_id:
                    existing.setdefault(value, f_plan_id)
    return existing


def published_contract_ids() -> set:
    """Return every CMS contract ID already published under the output directory.

    Used to report contracts that were seeded by an earlier run but no longer
    appear in any source file, because their contracts have ended.  The seed
    never deletes files, so those files stay on disk; surfacing them keeps the
    staleness visible instead of silent.
    """
    contract_ids = set()
    if not os.path.isdir(OUTPUT_BASE_DIR):
        return contract_ids
    for payer_dir in sorted(os.listdir(OUTPUT_BASE_DIR)):
        full_dir = os.path.join(OUTPUT_BASE_DIR, payer_dir)
        if not os.path.isdir(full_dir):
            continue
        for existing_name in sorted(os.listdir(full_dir)):
            if not existing_name.endswith(".well_known_payer.json"):
                continue
            try:
                with open(os.path.join(full_dir, existing_name), encoding="utf-8") as f:
                    existing_doc = json.load(f)
            except (json.JSONDecodeError, OSError):
                continue
            for id_entry in existing_doc.get("identifier", []):
                if id_entry.get("system") == SYSTEM_CMS_CONTRACT_ID:
                    value = id_entry.get("value")
                    if value:
                        contract_ids.add(value)
    return contract_ids


def directory_contains_curated_file(*, output_dir: str) -> bool:
    """Return True if *output_dir* holds any well-known file that is manually curated.

    A file is considered manually curated when its "is_seeded" flag is anything
    other than exactly true (false, absent, or unreadable JSON).  Because
    curated files may carry FPIs derived from different identifier systems
    (and therefore different filenames), the seed must check the whole payer
    directory — not just its own target filename — before writing anything.
    """
    if not os.path.isdir(output_dir):
        return False
    for existing_name in sorted(os.listdir(output_dir)):
        if not existing_name.endswith(".well_known_payer.json"):
            continue
        existing_path = os.path.join(output_dir, existing_name)
        try:
            with open(existing_path, encoding="utf-8") as existing_file:
                existing_doc = json.load(existing_file)
        except (json.JSONDecodeError, OSError):
            # Unreadable files are treated as curated so the seed stays hands-off.
            return True
        if existing_doc.get("is_seeded", False) is not True:
            return True
    return False


def write_output_file(doc, payer_name, fpi):
    """Write the well-known JSON document to the appropriate subdirectory under payer_index_files/medicare_advantage/.

    Overwrite policy:
      1. If the payer's directory contains ANY manually curated file (a file
         whose "is_seeded" flag is not exactly true), the seed skips the whole
         payer.  Curated files may use FPIs from different identifier systems,
         so their filenames will not match the seed's target filename — the
         directory-level check is what protects them.
      2. If the seed's own target file exists with is_seeded exactly true but
         contains fields beyond what the seed produces, it has been enriched
         and will NOT be overwritten.
    A warning is printed and the function returns (filepath, skipped=True) when skipping.
    """
    dir_name = safe_name(payer_name)
    output_dir = os.path.join(OUTPUT_BASE_DIR, dir_name)

    filename = f"{dir_name}_{fpi}.well_known_payer.json"
    filepath = os.path.join(output_dir, filename)

    # Guard 1: never touch a payer directory that holds manually curated files.
    if directory_contains_curated_file(output_dir=output_dir):
        print(f"    !! SKIPPED (directory contains manually curated file(s) — is_seeded not true):")
        return filepath, True

    os.makedirs(output_dir, exist_ok=True)

    if os.path.exists(filepath):
        try:
            with open(filepath, encoding="utf-8") as f:
                existing_doc = json.load(f)

            # Guard 2: check whether the file has grown beyond the seed's own fields.
            extra_fields = collect_extra_fields(existing_doc, doc)
            if extra_fields:
                print(f"    !! SKIPPED (file has grown beyond seed data):")
                for field in extra_fields:
                    print(f"       + {field}")
                return filepath, True
        except (json.JSONDecodeError, OSError) as exc:
            print(f"    !! WARNING: Could not read existing file for comparison ({exc}). Overwriting.")

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)
        f.write("\n")

    return filepath, False


def main():
    print("=" * 60)
    print("Medicare Advantage Well-Known JSON Seed Generator")
    print("(Payer-Name-Based FPI Mode)")
    print("=" * 60)
    print()
    print("Identifier strategy: FPI is derived from the normalized payer name")
    print("  (lowercase, all non-alphanumeric characters removed).")
    print("  Multiple contract IDs sharing the same normalized name are merged")
    print("  into a single well-known JSON file under one FPI.")
    print()
    print("Coverage: every contract in the CMS monthly report is seeded, for every")
    print("  Organization Type (CCP, PDP, PACE, Cost, HCPP, PFFS, MSA, LI NET).")
    print("  Payers with no usable endpoint URL get a file whose plan_group")
    print("  asserts no endpoint, so their FPI and plan roster are still published.")
    print()
    print("Endpoint keys written:")
    print(f"  FHIR API URL file     -> {ENDPOINT_KEY}")
    print(f"  MPF 'FHIR JSON'       -> {ALL_AT_ONCE_ENDPOINT_KEY}")
    print(f"  MPF 'Machine-readable'-> {MACHINE_READABLE_ENDPOINT_KEY}")
    print()
    print("Payer-level search strings: Organization Name, Organization Marketing")
    print("  Name and Parent Organization are published together in the FPI")
    print("  identifier's payer_level_string_search_matches list.")
    print()

    print(f"Loading CMS monthly report from:\n  {MONTHLY_REPORT_FILE}")
    monthly, monthly_stats = load_monthly_report(MONTHLY_REPORT_FILE)

    print(f"\nLoading FHIR provider directory API URLs from:\n  {FHIR_API_URL_FILE}")
    fhir_urls, fhir_stats = load_fhir_api_urls(FHIR_API_URL_FILE)

    print(f"\nLoading MPF provider directory URLs from:\n  {PAYER_URL_FILE}")
    mpf_urls, mpf_stats = load_mpf_urls(PAYER_URL_FILE)

    # Merge the three sources into one per-contract registry, then group the
    # contracts by normalized payer legal name.
    registry, registry_stats = build_contract_registry(monthly, fhir_urls, mpf_urls)
    name_groups = group_payers_by_name(registry)

    # Endpoint key coverage across the merged registry.
    endpoint_key_counts = {}
    for info in registry.values():
        for key in info["endpoints"]:
            endpoint_key_counts[key] = endpoint_key_counts.get(key, 0) + 1

    # Organization Type coverage, so the PACE/PDP population stays visible.
    org_type_counts = {}
    for info in registry.values():
        org_type_counts[info["org_type"] or "(not in monthly report)"] = (
            org_type_counts.get(info["org_type"] or "(not in monthly report)", 0) + 1
        )

    print(f"\nOutput directory:\n  {OUTPUT_BASE_DIR}")
    print(f"\nContracts in the registry:   {len(registry)}")
    print(f"Unique payer names (groups): {len(name_groups)}")
    print(f"  → {len(registry) - len(name_groups)} contract(s) consolidated by shared name")
    print()

    files_written = 0
    files_skipped_enriched = 0
    payers_no_plans = 0
    files_without_endpoint = 0

    for normalized_name, group in sorted(name_groups.items()):
        canonical_name = group["canonical_name"]
        contract_entries = group["contracts"]

        # A payer with no plans at all is still worth reporting, but it is not a
        # reason to skip the file: the FPI, contract IDs and any known endpoint
        # are still published.
        total_plans_available = sum(
            len([p for p in e["plans"] if p["plan_id"]]) for e in contract_entries
        )
        if total_plans_available == 0:
            payers_no_plans += 1

        # Reuse f_plan_id values already published for this payer so that
        # re-running the seed does not churn every existing plan entry.
        payer_dir = os.path.join(OUTPUT_BASE_DIR, safe_name(canonical_name))
        existing_f_plan_ids = load_existing_f_plan_ids(output_dir=payer_dir)

        doc, fpi, plan_count = build_well_known_json(
            normalized_name, canonical_name, contract_entries,
            search_matches=group["search_matches"],
            existing_f_plan_ids=existing_f_plan_ids,
        )
        filepath, skipped = write_output_file(doc, canonical_name, fpi)

        contract_ids = ", ".join(e["contract_id"] for e in contract_entries)
        print(f"  [{contract_ids}] {canonical_name}")
        print(f"    -> {os.path.relpath(filepath, REPO_ROOT)}")

        if skipped:
            files_skipped_enriched += 1
            print(f"       Plans: {plan_count}, FPI: {fpi}  [NOT overwritten — enriched beyond seed]")
        else:
            files_written += 1
            n_contracts = len(contract_entries)
            n_groups = len(doc["plan_groups"])
            endpoint_keys = sorted({
                key for g in doc["plan_groups"] for key in g["plan_endpoints"]
            })
            if not endpoint_keys:
                files_without_endpoint += 1
            plan_note = "" if plan_count else "  [no plans]"
            endpoint_note = (f"  Endpoints: {len(endpoint_keys)}"
                             if endpoint_keys else "  [no endpoint known]")
            print(f"       Contracts: {n_contracts}, Plan groups: {n_groups}, "
                  f"Plans: {plan_count}, FPI: {fpi}{plan_note}{endpoint_note}")

    # Contracts published in an earlier run that no longer appear in any source
    # file.  The seed never deletes files, so these persist on disk as orphans.
    # They are reported rather than removed: deletion should be a deliberate,
    # separate act.
    orphan_contracts = sorted(published_contract_ids() - set(registry))

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("  CMS monthly report (plan and payer census)")
    print(f"    Plan level rows read:                {monthly_stats['rows']}")
    print(f"    Rows with no contract number:        {monthly_stats['skipped_no_contract']}")
    print(f"    Rows with an empty Plan ID:          {monthly_stats['rows_without_plan_id']}")
    print(f"    Contracts found:                     {len(monthly)}")
    print(f"    Contract/column name conflicts:      {len(monthly_stats['name_conflicts'])}")
    for contract_id, column, established, found in monthly_stats["name_conflicts"][:5]:
        print(f"      [{contract_id}] {column}: \"{established}\" vs \"{found}\"")
    print()
    print("  FHIR provider directory API URL file")
    print(f"    Rows read:                           {fhir_stats['total']}")
    print(f"    Rows with no contract ID / name:     {fhir_stats['skipped_no_contract_id']}")
    print(f"    Usable API URLs:                     {fhir_stats['with_url']}")
    print(f"    Empty URL cells:                     {fhir_stats['no_url']}")
    print(f"    Multiple URLs (not published):       {fhir_stats['multi_url']}")
    print()
    print("  MPF provider directory URL file")
    print(f"    Rows read:                           {mpf_stats['total']}")
    print(f"    Rows with no contract ID / name:     {mpf_stats['skipped_no_contract_id']}")
    print(f"    'FHIR JSON' (all-at-once) URLs:      {mpf_stats['all_at_once']}")
    print(f"    'Machine-readable JSON' URLs:        {mpf_stats['machine_readable']}")
    print(f"    Empty URL cells:                     {mpf_stats['no_url']}")
    print(f"    Multiple URLs (not published):       {mpf_stats['multi_url']}")
    print(f"    Unrecognised Response Format:        {mpf_stats['unknown_format']}")
    print()
    print("  Merged contract registry")
    print(f"    Contracts seeded:                    {len(registry)}")
    print(f"    ...from the monthly report only:     {registry_stats['monthly_only_contracts']}")
    print(f"    ...from a URL file only (ended):     {len(registry_stats['url_only_contracts'])}")
    if registry_stats["url_only_contracts"]:
        preview = ", ".join(registry_stats["url_only_contracts"][:12])
        suffix = ", ..." if len(registry_stats["url_only_contracts"]) > 12 else ""
        print(f"      {preview}{suffix}")
    print(f"    Legal name disagreements:            {len(registry_stats['name_disagreements'])}")
    for contract_id, monthly_name, url_name in registry_stats["name_disagreements"][:5]:
        print(f"      [{contract_id}] report: \"{monthly_name}\"")
        print(f"                  url file: \"{url_name}\"  (report wins)")
    if registry_stats["no_legal_name"]:
        print(f"    Contracts with no legal name:        {len(registry_stats['no_legal_name'])}")
        print(f"      Not seeded: the FPI is a hash of the payer legal name, and a")
        print(f"      contract ID must never be used as an FPI source.")
    print()
    print("  Endpoint coverage (contracts carrying each key)")
    for key in (ENDPOINT_KEY, ALL_AT_ONCE_ENDPOINT_KEY, MACHINE_READABLE_ENDPOINT_KEY):
        print(f"    {endpoint_key_counts.get(key, 0):5d}  {key}")
    print(f"    {sum(1 for i in registry.values() if not i['endpoints']):5d}  (no endpoint known)")
    print()
    print("  Organization Type coverage")
    for org_type, count in sorted(org_type_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"    {count:5d}  {org_type}")
    print()
    print("  Output")
    print(f"    Unique normalized payer names:       {len(name_groups)}")
    print(f"    Contracts merged by shared name:     {len(registry) - len(name_groups)}")
    print(f"    Payer names with no plans:           {payers_no_plans}")
    print(f"    Well-known JSON files written:       {files_written}")
    print(f"    ...of those, asserting no endpoint:  {files_without_endpoint}")
    print(f"    Skipped (enriched beyond seed data): {files_skipped_enriched}")
    print()
    print("  Previously published contracts no longer in any source file")
    print(f"    Contracts: {len(orphan_contracts)}")
    if orphan_contracts:
        preview = ", ".join(orphan_contracts[:12])
        suffix = ", ..." if len(orphan_contracts) > 12 else ""
        print(f"      {preview}{suffix}")
        print(f"    Their contracts have ended.  The seed never deletes files, so")
        print(f"    these remain on disk; removing them should be a deliberate act.")
    print()


if __name__ == "__main__":
    main()
