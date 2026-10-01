# Federated Payer Identifiers — Payer-Selected Legacy Enumeration

Every payer selects a single legacy identifier that it already holds and
derives its
**[UUID](https://en.wikipedia.org/wiki/Universally_unique_identifier)** FPI
from that identifier. Once registered, CMS enforces the payer's selection.

The FPI identifies the legal payer entity that holds the relevant insurance
assets and liability for a beneficiary population. Ownership alone does not
combine legally and financially distinct payer entities into one FPI. This is
important when payers own payers through multiple levels or insure payer risk
through insurance and reinsurance arrangements. Those relationships do not
replace the assets, liability, and beneficiary-population identity boundary.

A payer chooses **which legacy identifier** anchors its FPI; neither this
repository nor NPD selects the source identifier on the payer's behalf. The
payer does not choose the UUID itself — the UUID is always computed from the
selected identifier. This is what is meant by **payer-selected legacy
enumeration**.

There is exactly one supported method:

**Existing legacy identifier → UUIDv5**

## Why a payer cannot mint its own UUID

Earlier drafts of this document also allowed a payer to generate a brand-new
UUID when it did not wish to reuse an identifier it already held. That option
has been removed. An FPI must be independently reproducible and auditable from
a declared source identifier: any consumer must be able to recompute the FPI
and get the same value. A randomly generated UUID has no verifiable linkage to
the legal payer entity, cannot be recomputed by a third party, and leaves the
registration process with nothing to verify beyond uniqueness. See
[Deprecating Newly Generated Identifiers](AI_Instructions/DeprecatingNewIdentifiers.md).

Registration checks that the FPI is syntactically valid, that it recomputes
from its declared source identifier, and that it has not already been claimed.
Registration does not make FPIs generated from different source identifiers
converge.

---

## Overview

```mermaid
flowchart LR

A["Existing<br/>Payer Identifier"]
B["Identifier System ID"]
C["Generate UUIDv5"]

F["Registration Check"]
G["Registered FPI"]

A --> B --> C --> F
F --> G
```

---

## Deriving the FPI (UUIDv5)

This is the only supported method. The payer selects a legacy identifier that
was assigned to it by a recognized authority and derives its FPI from that
identifier.

### 1. Select the Identifier System

UUIDv5 generation in this repository is supported for the enumerated payer
identifier systems. The payer decides which one of these identifiers to use.
Different choices intentionally produce different UUIDs.

Examples include:

| Identifier System ID | Assigning Authority | Status |
|----------------------|---------------------|--------|
| `HIOS_ID` | CMS | Active |
| `CMS_CONTRACT_ID` | CMS | Active |
| `STATE_MCO_ID` | State Medicaid Agency | Active |
| `STATE_DOI_ID` | State Department of Insurance | Active |
| `NAIC_ID` | NAIC | Active |
| `X12_PAYER_ID_AVAILITY` | Availity | Active |
| `LEI` | GLEIF | Active |
| ... | Additional enumerated identifier systems | |

> Only enumerated Payer Identifier System IDs may be used with this
> repository's UUIDv5 tooling.

> **Caution on `CMS_CONTRACT_ID`:** contract numbers identify *contracts*, not payer legal entities. One payer can hold many contracts, and contracts can move between payers. This repository's automated seeding therefore never derives an FPI from a contract number (it uses `LEGAL_NAME_HASH` instead — see below). A payer may still *elect* one of its own contract numbers as its preeminent identifier and derive its FPI from it, but that is the payer's choice, never a tooling default.

The list of enumerated Payer Identifier Systems is in
[`reference_data/current_payer_identification_systems.json`](reference_data/current_payer_identification_systems.json).
To propose another system, submit a pull request that adds it to that file.

### If a payer has no listed identifier

A payer that does not hold an identifier in any currently enumerated system
must not mint a UUID of its own. It has two options:

1. Use another enumerated system in which it *does* hold an identifier; or
2. Submit a pull request adding its identifier system to
   [`reference_data/current_payer_identification_systems.json`](reference_data/current_payer_identification_systems.json),
   and then derive its FPI from that newly enumerated system.

Note that the FPI itself (`FPI`) is also listed in that file as a payer identifier system, so that FPIs can be recorded and crosswalked alongside every other payer identifier. However, the `FPI` system may **not** be used as an FPI source namespace — you cannot derive an FPI from another FPI, and the FPI Maker CLI excludes it from the selectable namespaces.

In a payer well-known index, only the single FPI entry may carry
`fpi_source_system` and `fpi_source_value`. Those fields record how that FPI was
generated. Other entries in the identifier list are payer routing and crosswalk
identifiers and must not carry FPI-generation source fields.

### State-level identifier systems require a state prefix

Some identifier systems (currently `STATE_DOI_ID` and `STATE_MCO_ID`) are assigned by individual states, and their values are only unique *within* a single state. Texas DOI number `68775` and some other state's DOI number `68775` would otherwise hash to the same FPI.

To prevent these collisions, values from state-level identifier systems MUST be prefixed with the two-letter USPS state code and a hyphen before the UUIDv5 is generated:

```
TX-68775   (Texas DOI number 68775)
OH-12345   (Ohio DOI number 12345)
```

The FPI Maker CLI prompts for the state code automatically for these systems, and the `generate_fpi` library function rejects unprefixed state-level values.

### The `LEGAL_NAME_HASH` system requires name normalization

The `LEGAL_NAME_HASH` system hashes a payer's legal name. It exists as a temporary seeding hack: the legal name is the only payer attribute reliably available to CMS at seed time, so the Medicare Advantage seeder derives its initial FPIs from it. Payers are expected to replace these seeded FPIs with FPIs derived from real identifier systems (`NAIC_ID`, `HIOS_ID`, `LEI`, a state-prefixed `STATE_DOI_ID`, etc.).

Before hashing, the legal name is always normalized:

```text
lowercase the name, then remove every character that is not a-z or 0-9
"AETNA HEALTH, INC."  →  "aetnahealthinc"
```

This normalization is implemented once, inside `tools/FPI_maker_cli.py` (`normalize_legal_name`), and `generate_fpi` applies it automatically whenever `system_id == "LEGAL_NAME_HASH"` — so passing the raw legal name and the pre-normalized name produce the same FPI. Callers must never reimplement this normalization.

### 2. Generate the UUID

> **Recommended:** Use the provided CLI tool to generate FPIs correctly:
>
> ```bash
> python tools/FPI_maker_cli.py
> ```
>
> The tool guides you through selecting an identifier system and entering the payer ID value, then prints the generated FPI and the exact Python code needed to reproduce it.

FPI generation uses a **two-step chained UUIDv5** process, not a single `UUIDv5(namespace, value)` call. The identifier system ID is itself first hashed into a UUID5 namespace (using `NAMESPACE_DNS` as the root), and then the payer's identifier value is hashed using that derived namespace:

```
step_1: system_namespace = UUIDv5(NAMESPACE_DNS, "<SYSTEM_ID>.fhir")
step_2: fpi             = UUIDv5(system_namespace, "<payer_id_value>")
```

For state-level systems, the `<payer_id_value>` must already carry the two-letter state prefix (e.g. `"TX-68775"`), as described above.

Example in Python (for `HIOS_ID` / `"987654"`):

```python
import uuid

system_namespace = uuid.uuid5(uuid.NAMESPACE_DNS, "HIOS_ID.fhir")
fpi = str(uuid.uuid5(system_namespace, "987654"))
print(fpi)
```

The `.fhir` suffix is appended to the system ID string before hashing in step 1 — this is a deliberate namespacing convention to avoid collisions with other uses of `NAMESPACE_DNS`.

All FPI uuid generation logic in this repository lives in exactly one place: `tools/FPI_maker_cli.py`. Other tools (including the Medicare Advantage seeder) import from it rather than reimplementing the hashing. Its correctness is validated by the test suite in `tools/tests/test_FPI_maker_cli.py`:

```bash
python3 tools/tests/test_FPI_maker_cli.py
```

UUIDv5 is deterministic:

- Same Identifier System ID + same identifier value → same UUID every time
- Different Identifier System ID or identifier value → different UUID

---

## Registration Check

Every FPI follows the same registration process.

```text
Normalize UUID
      ↓
Recompute from fpi_source_system + fpi_source_value
      ↓
Matches?
   ├── No  → Reject
   └── Yes ↓
Check Registry
      ↓
Already Claimed?
   ├── No  → Register FPI
   └── Yes → Resolve collision with the payer
```

The registration process normalizes and validates UUID syntax, verifies that
the FPI recomputes from its declared source identifier, and rejects an
already-claimed value. It records and republishes the payer's choice; it does
not return a replacement canonical UUID or infer that two different FPIs refer
to the same payer.

During the initial implementation, this repository is the trusted working
copy. NPD is expected to republish accepted payer and endpoint data. The future
operational registration and enforcement workflow is not yet implemented here.
See [Future Steps](FutureSteps.md).

---

## Key Principles

- **Always** use **UUIDv5** derived from a payer-selected legacy identifier. There is no other supported mechanism; a payer may not mint its own UUID.
- UUIDv5 generation uses a **two-step chained process**: first derive a `system_namespace` via `uuid5(NAMESPACE_DNS, "<SYSTEM_ID>.fhir")`, then compute the FPI via `uuid5(system_namespace, "<payer_id_value>")`.
- Use **`python tools/FPI_maker_cli.py`** to generate FPIs correctly — it handles the two-step chaining automatically, and loads the enumerated identifier systems at runtime from `reference_data/current_payer_identification_systems.json`.
- UUIDv5 generation with this repository's tooling requires an enumerated **Identifier System ID** and the payer's identifier value.
- **All FPI hashing logic lives in one place** — `tools/FPI_maker_cli.py` — and is validated by `tools/tests/test_FPI_maker_cli.py`. Never reimplement it.
- **`LEGAL_NAME_HASH` values are always normalized** (lowercased, all non a-z0-9 characters removed) inside `FPI_maker_cli` before hashing. It is a temporary seeding hack; payers should replace name-hash FPIs with FPIs from real identifier systems.
- **Never default to `CMS_CONTRACT_ID` as an FPI source** — contract numbers identify contracts, not payer entities. A payer may elect a contract number as its preeminent identifier, but tooling never assumes it.
- **State-level identifier values** (e.g. `STATE_DOI_ID`, `STATE_MCO_ID`) must be prefixed with the two-letter USPS state code and a hyphen (e.g. `TX-68775`) before hashing, to prevent collisions between states.
- The **FPI itself is listed** in the payer identifier systems file so it can be crosswalked like any other identifier, but it may not be used as an FPI source namespace — you cannot derive an FPI from another FPI.
- **`fpi_source_system` and `fpi_source_value` are required** on every FPI entry. An FPI that cannot be recomputed from its declared source is invalid.
- The payer's choice of a source identifier is not a ranking of identifier systems.
- FPIs based on different source identifiers do not converge automatically.
- Registration rejects a UUID already claimed as an FPI but does not perform entity resolution.
