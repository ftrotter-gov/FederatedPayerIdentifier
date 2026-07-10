#!/usr/bin/env python3
"""
FPI Maker — CLI and library for generating Federated Payer Identifiers (FPIs).

Each payer identifier namespace derives a deterministic UUID5 by chaining from
NAMESPACE_DNS, exactly as the Medicare Advantage seed does:

    system_uuid = uuid5(NAMESPACE_DNS, "<SYSTEM_ID>.fhir")
    fpi         = uuid5(system_uuid,   "<payer_id_value>")

Usage as a library
------------------
    from tools.FPI_maker_cli import generate_fpi, PAYER_SYSTEMS

    fpi = generate_fpi("CMS_CONTRACT_ID", "H1234")
    print(fpi)

Usage as a CLI
--------------
    python tools/FPI_maker_cli.py
"""

import uuid

# ---------------------------------------------------------------------------
# Payer identifier systems — sourced from current_payer_identification_systems.json
# ---------------------------------------------------------------------------

PAYER_SYSTEMS = [
    {
        "id": "HIOS_ID",
        "label": "HIOS ID (Health Insurance Oversight System)",
        "acronym": "Health Insurance Oversight System",
        "assigning_authority": "CMS",
        "is_defunct": False,
        "description": (
            "A web-based application used by CMS. It acts as a central portal for state "
            "entities and private health insurance issuers to submit, collect, and manage "
            "plan and issuer data. HIOS Issuer IDs are commonly used to identify ACA "
            "Marketplace issuers."
        ),
        "example": "12345",
    },
    {
        "id": "CMS_CONTRACT_ID",
        "label": "CMS Contract ID (Medicare Advantage / Part D / Cost / PACE)",
        "acronym": "CMS Contract ID",
        "assigning_authority": "CMS",
        "is_defunct": False,
        "description": (
            "A Medicare Advantage, Part D, Cost Plan, PACE, or other CMS contract number. "
            "A unique alphanumeric identifier assigned by CMS to the organization operating "
            "the plan."
        ),
        "example": "H1234",
    },
    {
        "id": "MCO_ID",
        "label": "MCO ID (State Medicaid Managed Care Organization Identifier)",
        "acronym": "State Medicaid Managed Care Organization Identifier",
        "assigning_authority": "State Medicaid Agency",
        "is_defunct": False,
        "description": (
            "An identifier assigned by a state Medicaid program to a managed care "
            "organization or Medicaid plan."
        ),
        "example": "TX-MCO-9876",
    },
    {
        "id": "HPID",
        "label": "HPID (Health Plan Identifier) — DEFUNCT",
        "acronym": "Health Plan Identifier",
        "assigning_authority": "CMS",
        "is_defunct": True,
        "description": (
            "A retired identifier system created under the Affordable Care Act intended to "
            "provide a national identifier for health plans. Implementation was suspended "
            "and the identifier is no longer in active use."
        ),
        "example": "1234567890",
    },
    {
        "id": "NAIC_ID",
        "label": "NAIC ID (National Association of Insurance Commissioners Company Code)",
        "acronym": "National Association of Insurance Commissioners Company Code",
        "assigning_authority": "NAIC",
        "is_defunct": False,
        "description": (
            "A unique numeric code assigned to insurance company legal entities regulated "
            "by state insurance departments."
        ),
        "example": "12345",
    },
    {
        "id": "EIN",
        "label": "EIN (Employer Identification Number)",
        "acronym": "Employer Identification Number",
        "assigning_authority": "IRS",
        "is_defunct": False,
        "description": (
            "A federal tax identifier assigned to organizations. Often used as a payer "
            "identifier for self-funded ERISA plans and employer-sponsored health plans."
        ),
        "example": "12-3456789",
    },
    {
        "id": "LEI",
        "label": "LEI (Legal Entity Identifier)",
        "acronym": "Legal Entity Identifier",
        "assigning_authority": "GLEIF",
        "is_defunct": False,
        "description": (
            "A unique 20-character alphanumeric identifier used to identify legal entities "
            "participating in financial and business transactions."
        ),
        "example": "7H6GLXDRUGQFU57RNE97",
    },
    {
        "id": "vLEI",
        "label": "vLEI (Verifiable Legal Entity Identifier)",
        "acronym": "Verifiable Legal Entity Identifier",
        "assigning_authority": "GLEIF",
        "is_defunct": False,
        "description": (
            "A cryptographically verifiable digital form of the LEI that enables automated "
            "verification of organizational identity and authorized representatives."
        ),
        "example": "did:webs:gleif.org:vlei:7H6GLXDRUGQFU57RNE97",
    },
    {
        "id": "X12_PAYER_ID_OPTUM",
        "label": "X12 Payer ID — Optum",
        "acronym": "X12 Payer ID",
        "assigning_authority": "Optum",
        "is_defunct": False,
        "description": (
            "An X12 electronic transaction routing identifier assigned and maintained "
            "within the Optum clearinghouse ecosystem."
        ),
        "example": "SX033",
    },
    {
        "id": "X12_PAYER_ID_TRIZETTO",
        "label": "X12 Payer ID — TriZetto",
        "acronym": "X12 Payer ID",
        "assigning_authority": "TriZetto",
        "is_defunct": False,
        "description": (
            "An X12 electronic transaction routing identifier assigned and maintained "
            "within the TriZetto clearinghouse ecosystem."
        ),
        "example": "SX033",
    },
    {
        "id": "X12_PAYER_ID_AVAILITY",
        "label": "X12 Payer ID — Availity",
        "acronym": "X12 Payer ID",
        "assigning_authority": "Availity",
        "is_defunct": False,
        "description": (
            "An X12 electronic transaction routing identifier assigned and maintained "
            "within the Availity clearinghouse ecosystem."
        ),
        "example": "SX033",
    },
    {
        "id": "X12_PAYER_ID_CHANGE_HEALTHCARE",
        "label": "X12 Payer ID — Change Healthcare",
        "acronym": "X12 Payer ID",
        "assigning_authority": "Change Healthcare",
        "is_defunct": False,
        "description": (
            "An X12 electronic transaction routing identifier assigned and maintained "
            "within the Change Healthcare clearinghouse ecosystem."
        ),
        "example": "SX033",
    },
    {
        "id": "X12_PAYER_ID_EMDEON",
        "label": "X12 Payer ID — Emdeon",
        "acronym": "X12 Payer ID",
        "assigning_authority": "Emdeon",
        "is_defunct": False,
        "description": (
            "A legacy X12 electronic transaction routing identifier assigned within the "
            "Emdeon clearinghouse ecosystem."
        ),
        "example": "SX033",
    },
    {
        "id": "X12_PAYER_ID_WAYSTAR",
        "label": "X12 Payer ID — Waystar",
        "acronym": "X12 Payer ID",
        "assigning_authority": "Waystar",
        "is_defunct": False,
        "description": (
            "An X12 electronic transaction routing identifier assigned and maintained "
            "within the Waystar clearinghouse ecosystem."
        ),
        "example": "SX033",
    },
    {
        "id": "X12_PAYER_ID_ZELIS",
        "label": "X12 Payer ID — Zelis",
        "acronym": "X12 Payer ID",
        "assigning_authority": "Zelis",
        "is_defunct": False,
        "description": (
            "An X12 electronic transaction routing identifier assigned and maintained "
            "within the Zelis clearinghouse ecosystem."
        ),
        "example": "SX033",
    },
    {
        "id": "X12_PAYER_ID_OFFICE_ALLY",
        "label": "X12 Payer ID — Office Ally",
        "acronym": "X12 Payer ID",
        "assigning_authority": "Office Ally",
        "is_defunct": False,
        "description": (
            "An X12 electronic transaction routing identifier assigned and maintained "
            "within the Office Ally clearinghouse ecosystem."
        ),
        "example": "SX033",
    },
    {
        "id": "X12_PAYER_ID_SSI_GROUP",
        "label": "X12 Payer ID — SSI Group",
        "acronym": "X12 Payer ID",
        "assigning_authority": "SSI Group",
        "is_defunct": False,
        "description": (
            "An X12 electronic transaction routing identifier assigned and maintained "
            "within the SSI Group clearinghouse ecosystem."
        ),
        "example": "SX033",
    },
    {
        "id": "X12_ROUTING_NEIC_ID",
        "label": "X12 Routing NEIC ID (National Electronic Information Corporation) — DEFUNCT",
        "acronym": "National Electronic Information Corporation",
        "assigning_authority": "NEIC",
        "is_defunct": True,
        "description": (
            "A historical payer routing identifier from the National Electronic Information "
            "Corporation (NEIC), an early healthcare EDI network. Many systems still refer "
            "to payer IDs as 'NEIC IDs' even though the organization no longer exists."
        ),
        "example": "00192",
    },
    {
        "id": "NCPDP_PAYER_ID",
        "label": "NCPDP Payer ID (National Council for Prescription Drug Programs)",
        "acronym": "National Council for Prescription Drug Programs",
        "assigning_authority": "NCPDP",
        "is_defunct": False,
        "description": (
            "A payer identifier used within NCPDP pharmacy transaction standards. NCPDP "
            "identifiers are commonly used in pharmacy claims processing and pharmacy "
            "benefit management systems."
        ),
        "example": "004336",
    },
]

# ---------------------------------------------------------------------------
# Library API
# ---------------------------------------------------------------------------

# Root anchor — same as uuid.NAMESPACE_DNS, named explicitly for clarity.
_ROOT_NAMESPACE = uuid.NAMESPACE_DNS


def get_system_namespace(system_id: str) -> uuid.UUID:
    """
    Return the UUID5 namespace for a given payer identifier system ID.

    This mirrors the pattern used in seed.py for Medicare Advantage:

        MEDICARE_ADVANTAGE_SYSTEM_UUID = uuid5(NAMESPACE_DNS, "CMS_CONTRACT_ID.fhir")

    Every system follows the same pattern:

        system_uuid = uuid5(NAMESPACE_DNS, "<system_id>.fhir")
    """
    return uuid.uuid5(_ROOT_NAMESPACE, f"{system_id}.fhir")


def generate_fpi(system_id: str, payer_id_value: str) -> str:
    """
    Generate a deterministic Federated Payer Identifier (FPI) UUID5 string.

    Parameters
    ----------
    system_id : str
        One of the ``id`` values from PAYER_SYSTEMS, e.g. ``"CMS_CONTRACT_ID"``.
    payer_id_value : str
        The actual identifier value within that system, e.g. ``"H1234"``.

    Returns
    -------
    str
        A UUID5 string that is the FPI, e.g.
        ``"5e4c4d18-0725-58ce-9477-d8482ea11016"``.

    Example
    -------
        >>> from tools.FPI_maker_cli import generate_fpi
        >>> fpi = generate_fpi("CMS_CONTRACT_ID", "H0028")
        >>> print(fpi)
        5e4c4d18-0725-58ce-9477-d8482ea11016
    """
    system_namespace = get_system_namespace(system_id)
    return str(uuid.uuid5(system_namespace, payer_id_value))


def get_system_by_id(system_id: str) -> dict | None:
    """Return the PAYER_SYSTEMS entry for *system_id*, or None if not found."""
    for system in PAYER_SYSTEMS:
        if system["id"] == system_id:
            return system
    return None


# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------

def _print_separator(char: str = "─", width: int = 60) -> None:
    print(char * width)


def _prompt_system_choice() -> dict:
    """
    Interactively ask the user to pick a payer identifier namespace.
    Returns the chosen system dict from PAYER_SYSTEMS.
    """
    print()
    _print_separator()
    print("  FPI Maker — Federated Payer Identifier Generator")
    _print_separator()
    print()
    print("Available payer identifier namespaces:")
    print()

    for i, system in enumerate(PAYER_SYSTEMS, start=1):
        defunct_tag = "  [DEFUNCT]" if system["is_defunct"] else ""
        print(f"  {i:>2}. {system['label']}{defunct_tag}")

    print()

    while True:
        raw = input("Select a namespace by number: ").strip()
        if not raw.isdigit():
            print("  Please enter a number.")
            continue
        choice = int(raw)
        if 1 <= choice <= len(PAYER_SYSTEMS):
            return PAYER_SYSTEMS[choice - 1]
        print(f"  Please enter a number between 1 and {len(PAYER_SYSTEMS)}.")


def _prompt_payer_id(system: dict) -> str:
    """Prompt the user for the actual payer identifier value."""
    print()
    print(f"  System   : {system['label']}")
    print(f"  Authority: {system['assigning_authority']}")
    print(f"  About    : {system['description']}")
    if system.get("example"):
        print(f"  Example  : {system['example']}")
    if system["is_defunct"]:
        print("  ⚠️  NOTE: This identifier system is marked as DEFUNCT.")
    print()

    while True:
        raw = input(f"Enter the {system['id']} value: ").strip()
        if raw:
            return raw
        print("  Value cannot be empty. Please try again.")


def _print_result(system: dict, payer_id_value: str) -> None:
    """Print the generated FPI together with the Python code needed to reproduce it."""
    system_id = system["id"]
    system_namespace = get_system_namespace(system_id)
    fpi = generate_fpi(system_id, payer_id_value)

    print()
    _print_separator()
    print("  Python code to reproduce this FPI")
    _print_separator()
    print()
    print("    import uuid")
    print()
    print(f"    system_namespace = uuid.uuid5(uuid.NAMESPACE_DNS, \"{system_id}.fhir\")")
    print(f"    # system_namespace == uuid.UUID(\"{system_namespace}\")")
    print()
    print(f"    fpi = str(uuid.uuid5(system_namespace, \"{payer_id_value}\"))")
    print()
    _print_separator()
    print("  Generated FPI")
    _print_separator()
    print()
    print(f"    {fpi}")
    print()
    _print_separator()


def _run_again() -> bool:
    """Ask whether the user wants to generate another FPI."""
    print()
    raw = input("Generate another FPI? [y/N]: ").strip().lower()
    return raw in ("y", "yes")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Interactive CLI entry point."""
    while True:
        system = _prompt_system_choice()
        payer_id_value = _prompt_payer_id(system)
        _print_result(system, payer_id_value)

        if not _run_again():
            print()
            print("Goodbye.")
            print()
            break


if __name__ == "__main__":
    main()
