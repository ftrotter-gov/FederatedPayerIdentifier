# ![BETA](https://img.shields.io/badge/BETA-red) Federated Payer Identifier Specification

**Version:** Prototype / Draft 1

This specification defines how a United States healthcare payer enumerates
itself with a Federated Payer Identifier (FPI) and publishes a machine-readable
index connecting that identity to its plans, its other payer identifiers, and
its interoperability endpoints.

The index is retrieved from a payer-controlled location using a well-known URI,
following the pattern established by
[SMART App Launch](https://www.hl7.org/fhir/smart-app-launch/conformance.html#fhir-authorization-endpoint-and-capabilities-discovery-using-a-well-known-uniform-resource-identifiers-uris).
A consumer that knows nothing about a payer except one base URL can retrieve the
payer's legal identity, every identifier the payer is known by in commerce, every
plan the payer offers, and every endpoint serving those plans.

This document states the **hard requirements for conformance**. It is the
normative companion to the explanatory documents in this repository:

* [README](README.md) — identity and authority model, and the problems addressed.
* [Generating Federated Payer Identifiers](GeneratingFederatedPayerIdentifiers.md) — the FPI derivation procedure.
* [Payer Plan Well-Known Index JSON Format](WellKnownFileFormat.md) — the annotated field-by-field format description.
* [All at Once](AllAtOnce.md) — bulk provider directory publication.
* [Future Steps](FutureSteps.md) — capabilities deliberately out of scope.

Where this specification and an explanatory document disagree, this
specification governs.

This is an early prototype. Its formats and processes may change as the National
Provider Directory Implementation (NPD) of the FAST FHIR NDH IG standard evolves.

---

## Table of Contents

1. [Conformance Language](#1-conformance-language)
2. [Actors and Scope](#2-actors-and-scope)
3. [Discovery and Publication of the Payer Index](#3-discovery-and-publication-of-the-payer-index)
4. [The Federated Payer Identifier](#4-the-federated-payer-identifier)
5. [Legacy and Crosswalk Payer Identifiers](#5-legacy-and-crosswalk-payer-identifiers)
6. [Plan Groups](#6-plan-groups)
7. [Plan Identifiers](#7-plan-identifiers)
8. [Plan Endpoints](#8-plan-endpoints)
9. [Conformance Checklist](#9-conformance-checklist)
10. [Implementation Status](#10-implementation-status)
11. [Out of Scope](#11-out-of-scope)
12. [References, Authors, and Notices](#12-references-authors-and-notices)

---

## 1. Conformance Language

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**,
**SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL** in this
document are to be interpreted as described in
[RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) and
[RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) when, and only when, they
appear in all capitals. These words in lower case carry their ordinary English
meaning and impose no requirement.

Every normative statement in this specification carries a stable identifier of
the form `AREA-nnn`:

| Prefix | Area |
|--------|------|
| `WK-` | The well-known index file: discovery, transport, and document structure |
| `FPI-` | Federated Payer Identifier entries |
| `LEG-` | Legacy and crosswalk payer identifiers |
| `PG-` | Plan groups |
| `PLAN-` | Plan identifiers |
| `EP-` | Plan endpoints |

Requirement identifiers are stable once published. They are numbered in tens so
that later requirements can be inserted without renumbering. An identifier is
never reused for a different requirement; a withdrawn requirement is marked
withdrawn and its identifier is retired.

Requirement identifiers exist so that the validator described in
[Future Steps](FutureSteps.md) can cite the exact clause a file violates.

All examples in this document are **non-normative**. For readability, some
examples are abbreviated and omit fields that a conforming file would carry. The
one worked example maintained in this repository is
[`example_wellknown_payer_index.json`](example_wellknown_payer_index.json).

---

## 2. Actors and Scope

**Payer.** A legal entity that holds insurance assets and liability for a set of
beneficiaries. The payer selects its FPI source identifier and publishes the
index. The payer is the authority for its own identity data.

**Consumer.** Any party that retrieves and uses a payer index — a provider
system, an application developer, a directory aggregator, or a regulator.

**Registry.** The service that accepts an FPI claim, verifies it, and
republishes accepted content. During the prototype this repository is the
trusted working copy, and NPD is expected to republish accepted payer and
endpoint data. The registry does **not** select or generate a payer's FPI.

### 2.1 Identity boundary

The identity boundary is the legal payer entity that holds the relevant
insurance assets and liability for a set of beneficiaries.

**WK-005** — A legal payer entity SHOULD have one FPI in relation to one
liability and beneficiary set.

Ownership alone MUST NOT be used to collapse multiple payer entities into one
FPI. Insurance structures can include a payer that owns another payer, several
nested levels of payer ownership, and payers that insure payer risk through
insurance or reinsurance arrangements. Each entity's actual insurance assets,
liabilities, and beneficiary obligations — not the ownership chain by itself —
determine the FPI boundary. In the current version, representing those nested 
relationships is out of scope; see [Future Steps](FutureSteps.md).

### 2.2 What conformance means

A **conforming payer index** is a JSON document that satisfies every MUST and
MUST NOT in this specification. A **conforming payer** publishes a conforming
index at the location defined in Section 3.

Conformance is a property of the published document. A document that is
syntactically valid JSON but violates a semantic requirement in this
specification is not conforming.

---

## 3. Discovery and Publication of the Payer Index

Discovery follows the base-URL pattern defined by
[SMART App Launch](https://www.hl7.org/fhir/smart-app-launch/conformance.html#fhir-authorization-endpoint-and-capabilities-discovery-using-a-well-known-uniform-resource-identifiers-uris)
for `/.well-known/smart-configuration`, and the well-known URI mechanism of
[RFC 8615](https://www.rfc-editor.org/rfc/rfc8615).

### 3.1 The Payer Index Base URL

**WK-010** — A payer MUST designate one **Payer Index Base URL**. It MUST be an
absolute URL using the `https` scheme. It MAY include path components.

**WK-020** — A payer MUST serve its payer index at the location formed by
appending `/.well-known/payer-index` to its Payer Index Base URL.

**WK-030** — Contrary to RFC 8615 Appendix B.4, the `.well-known` path component
MAY be appended even when the Payer Index Base URL already contains a path
component. This mirrors the equivalent allowance in SMART App Launch.

WK-030 is what makes vendor-hosted publication possible. A payer that does not
control the root of a domain can still publish a conforming index beneath a path
that it does control.

*Non-normative examples:*

```
Base URL "payer.example.com"

  GET /.well-known/payer-index HTTP/1.1
  Host: payer.example.com


Base URL "vendor.example.com/payers/acme-health"

  GET /payers/acme-health/.well-known/payer-index HTTP/1.1
  Host: vendor.example.com
```

**WK-040** — The Payer Index Base URL SHOULD be controlled by the payer. It MAY
resolve to infrastructure operated by a vendor on the payer's behalf.

Domain control is a significant trust signal, but a strict same-domain rule
would reject legitimate vendor arrangements. This prototype does not define a
proof-of-control mechanism, does not require signatures, and does not require
automated TLS or domain-control validation. See
[Future Steps](FutureSteps.md).

### 3.2 Transport

**WK-050** — The payer index MUST be retrievable by an HTTP `GET` request to the
location defined in WK-020.

**WK-060** — Retrieval MUST NOT require authentication, authorization, or any
credential. The payer index is public data.

**WK-070** — The server MUST respond with a media type of `application/json`,
regardless of any `Accept` header supplied by the client. A client MAY omit the
`Accept` header, and a server MAY ignore any client-supplied `Accept` header.

**WK-080** — The response body MUST be a single JSON object encoded in UTF-8.

**WK-090** — The server SHOULD support Cross-Origin Resource Sharing (CORS) for
`GET` requests to the payer index, so that browser-based consumers can read it.

**WK-100** — Every URL appearing anywhere in the payer index MUST be an absolute
URL. Relative URLs MUST NOT be used.

WK-100 is deliberately stricter than SMART, which tolerates relative URLs from
legacy servers. A payer index has no single FHIR base URL to resolve against,
and its endpoint URLs routinely point at third-party vendor domains, so a
relative URL in this document has no well-defined meaning.

### 3.3 Document structure

**WK-110** — The payer index MUST contain an `identifier` array with at least
one entry.

**WK-120** — The payer index MUST contain a `plan_groups` array. It MAY be
empty if the payer currently offers no plans.

**WK-130** — The payer index MUST contain a `resourceType` member.

**WK-140** — The payer index MUST contain a `copied_from_url` member. Its value
MUST be either `null` or the absolute URL from which the working copy was
retrieved, as resolved under WK-020.

A `copied_from_url` of `null` means the document has not been retrieved from a
payer-controlled location — for example, a record seeded into this repository
from public CMS data. A non-null value records provenance.

**WK-150** — The payer index MAY contain an `is_seeded` Boolean. See
Section 10.

**WK-160** — `payerLegalName`, `payerContactWebsite`, and
`payer_level_string_search_matches` MUST NOT appear at the root of the document.
They are properties of an individual FPI entry; see Section 4.4.

*Non-normative skeleton:*

```json
{
  "copied_from_url": "https://payer.example.com/.well-known/payer-index",
  "resourceType": "http://hl7.org/fhir/us/fast-ndh/StructureDefinition/NDHPayerWellknownDefinition",
  "is_seeded": false,
  "identifier": [ "..." ],
  "plan_groups": [ "..." ]
}
```

### 3.4 Repository working copies

Within this repository, payer indexes are stored under
[`payer_index_files/`](payer_index_files) using the filename convention
`<payer_slug>_<fpi_uuid>.well_known_payer.json`.

That convention is a **non-normative** repository storage detail. It is not part
of the published format, and a payer MUST NOT be expected to serve its index at
a URL derived from it. Publication location is governed solely by WK-010 through
WK-030.

---

## 4. The Federated Payer Identifier

The first thing a payer index asserts is who the payer is. Everything else in
the document — every legacy identifier, every plan, every endpoint — hangs off
an FPI.

The derivation procedure is specified in
[Generating Federated Payer Identifiers](GeneratingFederatedPayerIdentifiers.md).
This section states the requirements the published document must satisfy; it
does not restate the procedure.

### 4.1 At least one FPI

**FPI-010** — A conforming payer index MUST contain at least one entry in
`identifier` for which `is_fpi` is `true`.

**FPI-020** — A payer index MAY contain more than one FPI entry. Multiple FPI
entries are appropriate when several legal payer entities share a common
technical or organizational publishing location.

**FPI-030** — Every FPI entry MUST appear in the `identifier` array **before**
any identifier entry that references it through `parent_fpi`.

FPI-030 means a reader encounters each FPI before the identifiers that depend on
it, and it allows a single-pass consumer to resolve every `parent_fpi` reference
without buffering the whole array.

### 4.2 Identifying an FPI entry

**FPI-040** — An FPI entry MUST carry the `system` value
`https://directory.cms.gov/payer_identification_system/fpi`.

**FPI-050** — Every entry in `identifier` MUST contain an `is_fpi` member whose
value is the Boolean `true` or `false`. It MUST NOT be a string, a number, or
`null`, and it MUST NOT be omitted.

**FPI-060** — An entry whose `system` is the FPI system MUST have `is_fpi` set
to `true`. An entry with any other `system` MUST have `is_fpi` set to `false`.

### 4.3 The FPI value

**FPI-070** — The `value` of an FPI entry MUST be a UUID in canonical lowercase
hyphenated form.

**FPI-080** — The `value` MUST be a UUIDv5 derived from a legacy identifier
selected by the payer, using the two-step derivation specified in
[Generating Federated Payer Identifiers](GeneratingFederatedPayerIdentifiers.md).

**FPI-090** — A payer MUST NOT mint a randomly generated UUID as its FPI. A
UUIDv4 or any other non-derived UUID MUST NOT appear as an FPI `value`.

An FPI must be independently reproducible and auditable. Any consumer must be
able to recompute it and obtain the same value. A randomly generated UUID has no
verifiable linkage to the legal payer entity and leaves registration with
nothing to verify beyond uniqueness. See
[Deprecating Newly Generated Identifiers](AI_Instructions/DeprecatingNewIdentifiers.md).

**FPI-100** — Every FPI entry MUST contain `fpi_source_system` and
`fpi_source_value`.

**FPI-110** — `fpi_source_system` MUST be one of the `system` URLs listed in
[`reference_data/current_payer_identification_systems.json`](reference_data/current_payer_identification_systems.json).

**FPI-120** — `fpi_source_system` MUST NOT be the FPI system itself. An FPI
MUST NOT be derived from another FPI.

**FPI-130** — The FPI `value` MUST be reproducible from its declared
`fpi_source_system` and `fpi_source_value` using
[`tools/FPI_maker_cli.py`](tools/FPI_maker_cli.py). An FPI that does not
recompute from its declared source is invalid.

**FPI-140** — For a state-scoped identifier system such as `STATE_DOI_ID` or
`STATE_MCO_ID`, `fpi_source_value` MUST carry the two-letter USPS state code and
a hyphen as a prefix, for example `TX-68775`.

**FPI-150** — A payer SHOULD NOT derive its FPI from `CMS_CONTRACT_ID`.
Contract numbers identify contracts, not payer legal entities: one payer can
hold many contracts, and contracts can move between payers. A payer MAY elect a
contract number as its preeminent identifier, but tooling MUST NOT default to
one.

**FPI-160** — Each FPI `value` MUST be unique within the document. Two entries
with `is_fpi: true` MUST NOT share a `value`.

### 4.4 Payer attributes carried by the FPI entry

Each FPI describes one legal payer entity, so the entity's descriptive
attributes live inside the FPI entry rather than at the document root.

**FPI-170** — Every FPI entry MUST contain `payerLegalName`, a non-empty string
giving the legal name of the payer entity the FPI identifies.

**FPI-180** — Every FPI entry MUST contain `payerContactWebsite`, an absolute
URL at which the payer can be contacted.

**FPI-190** — Every FPI entry MUST contain `payer_level_string_search_matches`,
an array of at least one non-empty string.

**FPI-200** — The strings in `payer_level_string_search_matches` MUST be those
that identify the payer entity **as a whole** when found on an insurance card,
an explanation of benefits, or a claim. Strings that identify an individual plan
MUST NOT be placed here; they belong in `plan_level_string_search_matches`
(Section 7.5).

*Non-normative example of a conforming FPI entry:*

```json
{
  "system": "https://directory.cms.gov/payer_identification_system/fpi",
  "value": "13e068e1-cd54-5baa-b7e3-79761afe7afc",
  "is_fpi": true,
  "payerLegalName": "Example Payer Legal Name, LLC",
  "payerContactWebsite": "https://example.com/our_contact_page/",
  "payer_level_string_search_matches": [
    "Example Payer Legal Name",
    "Example Payer",
    "EPL Insurance"
  ],
  "fpi_source_system": "https://directory.cms.gov/payer_identification_system/naic_id",
  "fpi_source_value": "12345"
}
```

### 4.5 Registration

**FPI-210** — A payer MUST NOT claim an FPI already claimed by a different
payer entity.

Registration normalizes and validates UUID syntax, verifies that the FPI
recomputes from its declared source identifier, and rejects an already-claimed
value. It records and republishes the payer's choice. It does not return a
replacement canonical UUID, and it does not infer that two different FPIs refer
to the same payer. FPIs derived from different source identifiers are not
expected to converge, and the choice of a source identifier is not a ranking of
identifier systems.

---

## 5. Legacy and Crosswalk Payer Identifiers

A payer is known in commerce by identifiers that long predate the FPI. Claims
are routed by them, directories are keyed to them, and trading partners look the
payer up by them. The payer index enumerates them so that a consumer holding any
one of them can resolve it to the payer's FPI.

### 5.1 Which identifiers to publish

**LEG-010** — A payer SHOULD publish, as a non-FPI identifier entry, every
identifier by which it is known in claims or in commerce.

**LEG-020** — A payer MUST publish, as a non-FPI identifier entry, any
identifier that uniquely and correctly identifies it and that is used as a
lookup mechanism by trading partners, providers, or clearinghouses.

**LEG-030** — The identifier a payer selected as its FPI source SHOULD also
appear as a non-FPI identifier entry in its own right, carrying the
`fpi_source_system` as its `system` and the `fpi_source_value` as its `value`.

LEG-030 keeps the crosswalk complete. A consumer searching the `identifier`
array for an NAIC code should find it as an identifier, without having to know
that it also happens to be the FPI derivation source.

### 5.2 Required members

**LEG-040** — Every non-FPI identifier entry MUST contain `system`, `value`,
`is_fpi`, and `parent_fpi`.

**LEG-050** — `system` MUST be one of the `system` URLs listed in
[`reference_data/current_payer_identification_systems.json`](reference_data/current_payer_identification_systems.json).

A payer holding an identifier in a system not yet enumerated there submits a
pull request adding that system. See [Future Steps](FutureSteps.md).

**LEG-060** — `is_fpi` MUST be `false` on every non-FPI identifier entry.

### 5.3 Parentage

**LEG-070** — Every identifier entry with `is_fpi: false` MUST contain
`parent_fpi`.

**LEG-080** — `parent_fpi` MUST reference exactly one FPI. Its value MUST be a
single string, never an array.

**LEG-090** — The value of `parent_fpi` MUST resolve to the `value` of an entry
in the **same document** for which `is_fpi` is `true`. A `parent_fpi` that
points at an FPI not declared in this document is invalid.

LEG-080 and LEG-090 together are what make the document self-contained: every
identifier in it belongs to one, and only one, payer entity declared in that
same document.

### 5.4 Prohibited members

**LEG-100** — A non-FPI identifier entry MUST NOT contain `fpi_source_system`
or `fpi_source_value`. Those members describe how an FPI was derived; they say
nothing about a routing identifier.

**LEG-110** — A non-FPI identifier entry MUST NOT contain `payerLegalName`,
`payerContactWebsite`, or `payer_level_string_search_matches`. Those are
properties of the FPI entry.

### 5.5 Optional members

**LEG-120** — An identifier entry MAY contain `notes`, a free-text string
describing the identifier or its provenance.

**LEG-130** — An identifier entry MAY contain `lookup_url`, an absolute URL at
which the identifier can be independently verified.

**LEG-140** — An identifier entry MAY contain `expiration`, whose value is
either the string `current` or the date on which the identifier ceased, or will
cease, to be valid.

*Non-normative example of a conforming crosswalk entry:*

```json
{
  "system": "https://directory.cms.gov/payer_identification_system/naic_id",
  "value": "12345",
  "is_fpi": false,
  "parent_fpi": "13e068e1-cd54-5baa-b7e3-79761afe7afc",
  "notes": "NAIC company code for Example Payer Legal Name, LLC.",
  "expiration": "current"
}
```

---

## 6. Plan Groups

A plan group collects the plans that share exactly the same set of production
endpoints. Grouping exists so that a payer with hundreds of plans served by one
set of FHIR endpoints does not repeat those endpoints hundreds of times.

### 6.1 Grouping rule

**PG-010** — The `plan_groups` member MUST be an array of objects.

**PG-020** — All plans listed in a single plan group MUST share exactly the same
set of production endpoints.

**PG-030** — Plans that do not share exactly the same set of production
endpoints MUST be placed in different plan groups.

**PG-040** — Plan group membership MUST be determined solely by the set of
**production** endpoints. Sandbox endpoints MUST NOT affect grouping: adding,
changing, or removing a sandbox URL MUST NOT split or merge a plan group.

### 6.2 Required members

**PG-050** — Every plan group MUST contain a `plan_identifiers` array with at
least one entry.

**PG-060** — Every plan group MUST contain a `plan_endpoints` object. It MAY be
empty when the payer publishes no production endpoints for those plans.

**PG-070** — Every plan group MUST contain `plan_group_string_search_match`, an
array of at least one non-empty string shared by every plan in the group.

**PG-080** — Strings that identify the payer entity as a whole MUST NOT be
placed in `plan_group_string_search_match`; they belong in the FPI entry's
`payer_level_string_search_matches` (FPI-200).

### 6.3 Relationship to the FPI

**PG-090** — All plans within a single plan group SHOULD reference the same FPI
through their `parent_fpi`.

**PG-100** — A payer index MAY contain multiple plan groups referencing
different FPIs, so that several legal payer entities published at one location
can each carry their own plans and endpoints.

---

## 7. Plan Identifiers

A plan identifier is how a consumer recognizes a specific insurance product —
from a card, a claim, or a directory — and resolves it to the payer that owns it
and the endpoints that serve it.

### 7.1 Identity members

**PLAN-010** — Every plan identifier MUST contain `system`, identifying the
enumeration system the plan identifier belongs to.

**PLAN-020** — Every plan identifier MUST contain `value`, the plan's identifier
within that system.

For the CMS Medicare plan system, `value` is the CMS contract ID and the plan
segment joined by a hyphen, for example `H1234-432`.

### 7.2 Parentage

**PLAN-030** — Every plan identifier MUST contain `parent_fpi`.

**PLAN-040** — `parent_fpi` MUST resolve to the `value` of an entry in the same
document for which `is_fpi` is `true`. It MUST reference exactly one FPI.

Every plan in a conforming document therefore names the legal payer entity that
owns it, using the same member name used on crosswalk identifiers (LEG-070).

### 7.3 The Federated Plan Identifier

`f_plan_id` is the Federated Plan Identifier. Where the FPI identifies the
contracting legal payer entity, `f_plan_id` identifies one specific plan entry.

**PLAN-050** — Every plan identifier MUST contain `f_plan_id`.

**PLAN-060** — `f_plan_id` MUST be a randomly generated UUID (UUIDv4) in
canonical lowercase hyphenated form. It MUST NOT be derived from any plan
attribute, and therefore MUST NOT encode plan name, contract ID, or any other
plan metadata.

**PLAN-070** — Each `f_plan_id` MUST be unique within the document. Two plan
identifier objects MUST NOT share an `f_plan_id`.

**PLAN-080** — `f_plan_id` MUST be stable over time. Once published for a plan,
it MUST NOT change in any later publication of the document, **including across
plan years**, even if the plan's `plan_name`, `plan_website`, endpoints, or
identifier `value` are revised.

**PLAN-090** — A new `f_plan_id` MUST be minted only for a plan that has not
previously been published.

**PLAN-100** — An `f_plan_id` belonging to a retired plan MUST NOT be reused for
a different plan.

Because the value is random it cannot be recomputed the way an FPI can, so its
stability depends entirely on the publisher carrying forward the value it
previously published. Consumers are expected to store `f_plan_id` as a durable
key; regenerating it breaks their references. Tooling in this repository
satisfies PLAN-080 through `load_existing_f_plan_ids()` in
`tools/seed_medicare_advantage/seed.py`, which reuses the `f_plan_id` already on
disk for each plan.

### 7.4 Descriptive members

**PLAN-110** — Every plan identifier MUST contain `plan_name`, a non-empty
string giving the plan's name as presented to consumers.

**PLAN-120** — Every plan identifier MUST contain `plan_website`, an absolute
URL for that specific plan.

### 7.5 Plan-level search matching

**PLAN-130** — Every plan identifier MUST contain
`plan_level_string_search_matches`, an array of **at least one** non-empty
string.

**PLAN-140** — The strings in `plan_level_string_search_matches` MUST be those
that identify this specific plan when found on an insurance card, an explanation
of benefits, or a claim.

**PLAN-150** — Each plan identifier MUST carry its own
`plan_level_string_search_matches`. Strings MAY overlap between plans, but each
plan maintains its own authoritative set.

*Non-normative example of a conforming plan identifier:*

```json
{
  "system": "https://directory.cms.gov/payer_identification_system/cms_contract_id/plan/plan_id",
  "value": "H1234-432",
  "parent_fpi": "13e068e1-cd54-5baa-b7e3-79761afe7afc",
  "f_plan_id": "a38f7115-9579-47ed-9ff0-65c084ec258c",
  "plan_name": "This Very Good Plan",
  "plan_website": "https://example.com/plan_432",
  "plan_level_string_search_matches": [
    "This Very Good Plan",
    "Very Good Plan Basic",
    "TVG Plan 432"
  ]
}
```

---

## 8. Plan Endpoints

Endpoints are the payload of the payer index. Everything preceding this section
exists so that a consumer can arrive here holding a plan or payer identifier and
leave with a URL it can call.

### 8.1 Production endpoints

**EP-010** — `plan_endpoints` MUST contain only **production** endpoints.

**EP-020** — `plan_endpoints` is the only object a consumer may use to route
live traffic.

**EP-030** — A payer MUST publish in `plan_endpoints` every interoperability
endpoint it operates for the plans in that plan group, including every endpoint
required of it by applicable CMS regulation.

EP-030 is deliberately stated by reference rather than by enumeration. The
endpoint families mandated of a given payer depend on regulations that change
over time — including the CMS Interoperability and Patient Access Final Rule
(CMS-9115-F) and the CMS Interoperability and Prior Authorization Final Rule
(CMS-0057-F) — and on which lines of business the payer operates. A fixed list
in this document would go stale. The requirement is that whatever a payer is
obliged to operate, it must also publish here.

### 8.2 Key grammar

**EP-040** — Each key in `plan_endpoints` MUST name an endpoint family,
optionally followed by a protocol version and a profile coordinate, for example
`carin_bluebutton_endpoint#1.0_uscore3.1`.

**EP-050** — Endpoint family names SHOULD be drawn from
[`reference_data/endpoint_types.json`](reference_data/endpoint_types.json),
which is aligned with the HL7 Da Vinci HRex
[Endpoint Name ValueSet](https://www.hl7.org/fhir/us/davinci-hrex/en/ValueSet-hrex-endpoint-name.html).

This prototype may define endpoint families not yet represented in that
ValueSet, including endpoints from other implementation guides and non-FHIR
interoperability resources such as Transparency in Coverage files.

**EP-060** — A version suffix such as `#1.1` denotes the version of the named
**protocol**, not the version of the payer index.

**EP-070** — Each protocol-and-version key MUST occur at most once within a
`plan_endpoints` object.

**EP-080** — Environment MUST NOT be encoded in a key name. A key such as
`davinci_pdex_payer_endpoint#1.1_sandbox` is invalid.

Environment, protocol version, and profile are three orthogonal axes. Collapsing
environment into the key would force every consumer to string-parse key names in
order to tell a test system from a live one.

**EP-090** — Omitting a key means the index makes no assertion for that protocol
and version. It MUST NOT be read as an assertion that the payer does not support
it.

### 8.3 Developer-facing URLs

**EP-100** — A payer MUST publish `ndh_meta_fhir_signup_url`, the absolute URL
at which a developer registers for access to the endpoints in this plan group.

**EP-110** — A payer MUST publish `ndh_meta_documentation_url`, the absolute URL
of the developer documentation for the endpoints in this plan group.

EP-100 and EP-110 are the developer website links. An endpoint a developer
cannot register for or learn to call is not usefully published.

These two keys are metadata URLs rather than callable API endpoints, and they
are not presently listed in
[`reference_data/endpoint_types.json`](reference_data/endpoint_types.json).
EP-050 is stated as SHOULD precisely to accommodate families of this kind;
adding them to the reference data is a known follow-up.

### 8.4 Sandbox endpoints

**EP-120** — Non-production endpoints MUST be published in a separate
`plan_endpoints_sandbox` object, sibling to `plan_endpoints`.

**EP-130** — `plan_endpoints_sandbox` is OPTIONAL. If a payer operates a sandbox
environment that external developers are invited to use, it MUST be published
there.

**EP-140** — `plan_endpoints_sandbox` MUST use the same key grammar as
`plan_endpoints` (EP-040 through EP-090).

**EP-150** — Keys in `plan_endpoints_sandbox` are independent of those in
`plan_endpoints`. A sandbox key MAY appear with no production counterpart, and a
production key MAY appear with no sandbox counterpart.

**EP-160** — A consumer MUST NOT treat a sandbox endpoint as a production
fallback. When a production key is absent or `null`, the correct conclusion is
that the index makes no assertion — not that the sandbox URL may be used
instead.

**EP-170** — `sandbox` is the only supported spelling for a non-production
environment. Variants such as `test`, `uat`, `stage`, `qa`, or `demo` MUST NOT
be used. A payer operating several internal tiers publishes whichever one
external developers are invited to use.

**EP-180** — Absence of `plan_endpoints_sandbox` means no assertion about
sandbox availability. It MUST NOT be read as an assertion that no sandbox
exists.

Sandbox endpoints may serve synthetic data, may be offline, and may discard data
without notice.

### 8.5 Bulk provider directory publication

**EP-190** — A payer publishing its provider directory in bulk MUST either
honor the FHIR Bulk Publish standard or provide simple HTTP access to NDJSON
exports conformant to the appropriate version of the Da Vinci PDex Plan-Net
implementation guide. See [All at Once](AllAtOnce.md).

*Non-normative example of a conforming endpoint pair:*

```json
{
  "plan_endpoints": {
    "davinci_crd_hook_endpoint#1.1": "https://example.org/foo/bar/crd",
    "davinci_pas_submission_endpoint#1.2": "https://example.org/foo/bar/pas2",
    "davinci_pdex_provider_directory_endpoint#1.1": "https://example.org/foo/bar/provider-directory",
    "davinci_pdex_payer_endpoint#1.1": "https://example.org/foo/bar/payer-to-payer",
    "carin_bluebutton_endpoint#1.0": "https://example.org/fhir/v3/patientaccess/",
    "ndh_meta_fhir_signup_url": "https://example.org/fhir_signup/",
    "ndh_meta_documentation_url": "https://example.org/fhir_docs/"
  },
  "plan_endpoints_sandbox": {
    "carin_bluebutton_endpoint#1.0": "https://sandbox.example.org/fhir/v3/patientaccess/",
    "ndh_meta_fhir_signup_url": "https://sandbox.example.org/fhir_signup/"
  }
}
```

---

## 9. Conformance Checklist

Every normative requirement in this specification, in one table. A conforming
payer satisfies every MUST and MUST NOT row.

### 9.1 Discovery and document structure

| ID | Level | Requirement |
|----|-------|-------------|
| WK-005 | SHOULD | One FPI per legal payer entity, per liability and beneficiary set |
| WK-010 | MUST | Designate one Payer Index Base URL, absolute and `https` |
| WK-020 | MUST | Serve the index at base URL + `/.well-known/payer-index` |
| WK-030 | MAY | Append `.well-known` even when the base URL has path components |
| WK-040 | SHOULD | Base URL controlled by the payer; MAY be vendor-hosted |
| WK-050 | MUST | Retrievable by HTTP `GET` |
| WK-060 | MUST NOT | Require authentication or any credential |
| WK-070 | MUST | Respond `application/json` regardless of `Accept` |
| WK-080 | MUST | Body is a single UTF-8 JSON object |
| WK-090 | SHOULD | Support CORS for `GET` |
| WK-100 | MUST | Every URL in the document is absolute |
| WK-110 | MUST | Contain `identifier` with at least one entry |
| WK-120 | MUST | Contain `plan_groups` |
| WK-130 | MUST | Contain `resourceType` |
| WK-140 | MUST | Contain `copied_from_url` (`null` or the retrieval URL) |
| WK-150 | MAY | Contain `is_seeded` |
| WK-160 | MUST NOT | Carry payer attributes at the document root |

### 9.2 Federated Payer Identifier

| ID | Level | Requirement |
|----|-------|-------------|
| FPI-010 | MUST | At least one `identifier` entry with `is_fpi: true` |
| FPI-020 | MAY | Contain more than one FPI entry |
| FPI-030 | MUST | Each FPI precedes the entries referencing it |
| FPI-040 | MUST | FPI entry carries the FPI `system` URL |
| FPI-050 | MUST | Every identifier entry contains a Boolean `is_fpi` |
| FPI-060 | MUST | `is_fpi` agrees with `system` |
| FPI-070 | MUST | FPI `value` is a canonical lowercase UUID |
| FPI-080 | MUST | FPI `value` is a UUIDv5 derived per the generation procedure |
| FPI-090 | MUST NOT | Mint a random UUID as an FPI |
| FPI-100 | MUST | FPI entry contains `fpi_source_system` and `fpi_source_value` |
| FPI-110 | MUST | `fpi_source_system` is an enumerated identifier system |
| FPI-120 | MUST NOT | Derive an FPI from another FPI |
| FPI-130 | MUST | FPI `value` recomputes from its declared source |
| FPI-140 | MUST | State-scoped source values carry the USPS state prefix |
| FPI-150 | SHOULD NOT | Derive an FPI from `CMS_CONTRACT_ID` |
| FPI-160 | MUST | Each FPI `value` is unique within the document |
| FPI-170 | MUST | FPI entry contains `payerLegalName` |
| FPI-180 | MUST | FPI entry contains `payerContactWebsite` |
| FPI-190 | MUST | FPI entry contains ≥1 `payer_level_string_search_matches` |
| FPI-200 | MUST | Payer-level strings identify the entity, not a plan |
| FPI-210 | MUST NOT | Claim an FPI already claimed by another payer |

### 9.3 Legacy and crosswalk identifiers

| ID | Level | Requirement |
|----|-------|-------------|
| LEG-010 | SHOULD | Publish every identifier used in claims or commerce |
| LEG-020 | MUST | Publish any identifier used as a payer lookup mechanism |
| LEG-030 | SHOULD | Publish the FPI source identifier as an identifier in its own right |
| LEG-040 | MUST | Contain `system`, `value`, `is_fpi`, `parent_fpi` |
| LEG-050 | MUST | `system` is an enumerated identifier system |
| LEG-060 | MUST | `is_fpi` is `false` |
| LEG-070 | MUST | Non-FPI entries contain `parent_fpi` |
| LEG-080 | MUST | `parent_fpi` references exactly one FPI, as a string |
| LEG-090 | MUST | `parent_fpi` resolves to an FPI in the same document |
| LEG-100 | MUST NOT | Carry `fpi_source_system` or `fpi_source_value` |
| LEG-110 | MUST NOT | Carry payer-level attributes |
| LEG-120 | MAY | Carry `notes` |
| LEG-130 | MAY | Carry `lookup_url` |
| LEG-140 | MAY | Carry `expiration` |

### 9.4 Plan groups and plan identifiers

| ID | Level | Requirement |
|----|-------|-------------|
| PG-010 | MUST | `plan_groups` is an array of objects |
| PG-020 | MUST | Plans in a group share exactly the same production endpoint set |
| PG-030 | MUST | Plans with differing endpoint sets occupy different groups |
| PG-040 | MUST | Grouping determined solely by production endpoints |
| PG-050 | MUST | Group contains ≥1 `plan_identifiers` entry |
| PG-060 | MUST | Group contains `plan_endpoints` |
| PG-070 | MUST | Group contains ≥1 `plan_group_string_search_match` |
| PG-080 | MUST NOT | Place payer-level strings in the group search list |
| PG-090 | SHOULD | All plans in a group share one `parent_fpi` |
| PG-100 | MAY | Different groups reference different FPIs |
| PLAN-010 | MUST | Plan identifier contains `system` |
| PLAN-020 | MUST | Plan identifier contains `value` |
| PLAN-030 | MUST | Plan identifier contains `parent_fpi` |
| PLAN-040 | MUST | `parent_fpi` resolves to one in-document FPI |
| PLAN-050 | MUST | Plan identifier contains `f_plan_id` |
| PLAN-060 | MUST | `f_plan_id` is a random canonical UUIDv4 |
| PLAN-070 | MUST | `f_plan_id` is unique within the document |
| PLAN-080 | MUST | `f_plan_id` is stable over time, including across plan years |
| PLAN-090 | MUST | Mint a new `f_plan_id` only for a previously unpublished plan |
| PLAN-100 | MUST NOT | Reuse a retired plan's `f_plan_id` |
| PLAN-110 | MUST | Plan identifier contains `plan_name` |
| PLAN-120 | MUST | Plan identifier contains `plan_website` |
| PLAN-130 | MUST | Plan identifier contains ≥1 `plan_level_string_search_matches` |
| PLAN-140 | MUST | Plan-level strings identify that specific plan |
| PLAN-150 | MUST | Each plan carries its own search-match list |

### 9.5 Endpoints

| ID | Level | Requirement |
|----|-------|-------------|
| EP-010 | MUST | `plan_endpoints` holds production endpoints only |
| EP-020 | — | `plan_endpoints` is the only routable object |
| EP-030 | MUST | Publish every operated and CMS-required endpoint |
| EP-040 | MUST | Keys follow the family/version/profile grammar |
| EP-050 | SHOULD | Family names drawn from `endpoint_types.json` |
| EP-060 | — | A version suffix versions the protocol, not the index |
| EP-070 | MUST | Each protocol-and-version key occurs at most once |
| EP-080 | MUST NOT | Encode environment in a key name |
| EP-090 | MUST NOT | Read an omitted key as non-support |
| EP-100 | MUST | Publish `ndh_meta_fhir_signup_url` |
| EP-110 | MUST | Publish `ndh_meta_documentation_url` |
| EP-120 | MUST | Non-production endpoints go in `plan_endpoints_sandbox` |
| EP-130 | MUST | Publish an externally-offered sandbox when one exists |
| EP-140 | MUST | Sandbox keys use the same grammar |
| EP-150 | MAY | Sandbox and production key sets differ |
| EP-160 | MUST NOT | Use a sandbox endpoint as a production fallback |
| EP-170 | MUST NOT | Use environment spellings other than `sandbox` |
| EP-180 | MUST NOT | Read an absent sandbox object as "no sandbox exists" |
| EP-190 | MUST | Bulk directory via FHIR Bulk Publish or conformant NDJSON |

---

## 10. Implementation Status

*This section is non-normative. It records the state of the data and tooling in
this repository at the time of writing, and is expected to change. Nothing here
relaxes a requirement in Sections 3 through 8.*

### 10.1 Seeded and curated records

A payer index MAY carry an `is_seeded` Boolean (WK-150):

* `true` marks uncurated output from an automated repository seeder.
* `false` marks a file reviewed or enriched by a person or curation process.

Seeding is a repository implementation detail, not part of the published
standard. General-purpose seeders must not overwrite curated payer directories,
and purpose-specific curation tools should preserve curated facts except for the
fields they exist to change.

### 10.2 Current corpus

The repository currently holds 788 payer index files: 784 data-bearing files and
4 pointer stubs that carry only a `new_file` reference to a renamed successor.

Every data-bearing file satisfies the structural identifier requirements —
`is_fpi` on every identifier entry, `parent_fpi` on every crosswalk identifier
and every plan identifier, every `parent_fpi` resolving to an in-document FPI,
and a unique `f_plan_id` on each of the 7,573 plan identifiers.

### 10.3 Known conformance gaps

Seeded files do not yet carry several fields this specification requires,
because the CMS source data used for seeding does not supply them. These files
are **not conforming** until curated:

| Requirement | Field | Status in seeded data |
|-------------|-------|------------------------|
| PLAN-120 | `plan_website` | Absent |
| PLAN-130 | `plan_level_string_search_matches` | Mostly absent |
| FPI-180 | `payerContactWebsite` | Absent |
| PG-070 | `plan_group_string_search_match` | Mostly absent |
| EP-100, EP-110 | `ndh_meta_fhir_signup_url`, `ndh_meta_documentation_url` | Present only where source endpoint data supplied them |
| WK-140 | `copied_from_url` | `null` throughout, since no file has yet been retrieved from a payer-controlled location |

This is a curation backlog, not a relaxation of the rules. The specification
states the target state; `is_seeded` exists so the distinction stays visible.

### 10.4 Temporary seeding mechanism

The Medicare Advantage seeder derives seed FPIs from `LEGAL_NAME_HASH` because
payer legal name is available in its source data. That mechanism does not define
permanent payer identity and is not a recommendation to payers. A payer selects
which supported legacy identifier anchors its FPI, and should replace a
name-hash FPI with one derived from a real identifier system.

---

## 11. Out of Scope

*This section is non-normative.*

The following are deliberately outside this prototype. Their absence is not an
omission, and implementers should not infer requirements about them from this
document. See [Future Steps](FutureSteps.md) for the full discussion.

* **Semantic validation tooling.** A Python validator is planned, which will
  cite the requirement identifiers defined in Section 1.
* **Historical identifiers and effective periods.** Git history is the current
  record-level snapshot mechanism.
* **Delegation between FPIs.** One FPI cannot presently delegate authority or
  operations to another.
* **Nested payer ownership and reinsurance.** The relationships among entities
  in a nested ownership chain are not represented.
* **Payers holding no enumerated identifier.** The current answer is a pull
  request adding the identifier system to
  [`reference_data/current_payer_identification_systems.json`](reference_data/current_payer_identification_systems.json).
* **Domain-control proof.** No signature, TLS, or automated domain-control
  validation is required for the Payer Index Base URL.
* **Payer-wide and plan-specific sandbox scopes.** `plan_endpoints_sandbox` is
  defined only at the plan group level.
* **Plan years and publication history.** Durable plan identity is addressed
  only by `f_plan_id` stability (PLAN-080); dated plan membership assertions are
  not yet modeled.

---

## 12. References, Authors, and Notices

### 12.1 Normative references

* Bradner, S., "Key words for use in RFCs to Indicate Requirement Levels",
  [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119), RFC Editor, March 1997.
* Leiba, B., "Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words",
  [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174), RFC Editor, May 2017.
* Nottingham, M., "Well-Known Uniform Resource Identifiers (URIs)",
  [RFC 8615](https://www.rfc-editor.org/rfc/rfc8615), RFC Editor, May 2019.
* Davis, K., Peabody, B., Leach, P., "Universally Unique IDentifiers (UUIDs)",
  [RFC 9562](https://www.rfc-editor.org/rfc/rfc9562), RFC Editor, May 2024.

### 12.2 Informative references

* HL7 International, "SMART App Launch — Conformance",
  [https://www.hl7.org/fhir/smart-app-launch/conformance.html](https://www.hl7.org/fhir/smart-app-launch/conformance.html).
* HL7 International, "Da Vinci Health Record Exchange (HRex) — Well-Known
  Endpoint",
  [https://build.fhir.org/ig/HL7/davinci-ehrx/en/Binary-Wellknown.html](https://build.fhir.org/ig/HL7/davinci-ehrx/en/Binary-Wellknown.html).
* HL7 International, "Da Vinci HRex Endpoint Name ValueSet",
  [https://www.hl7.org/fhir/us/davinci-hrex/en/ValueSet-hrex-endpoint-name.html](https://www.hl7.org/fhir/us/davinci-hrex/en/ValueSet-hrex-endpoint-name.html).
* HL7 International, "FAST National Directory of Healthcare Providers and
  Services (NDH) Implementation Guide",
  [https://build.fhir.org/ig/HL7/fhir-us-ndh/en/](https://build.fhir.org/ig/HL7/fhir-us-ndh/en/).
* HL7 International, "Da Vinci Payer Data Exchange (PDex) Plan-Net
  Implementation Guide",
  [https://hl7.org/fhir/us/davinci-pdex-plan-net/](https://hl7.org/fhir/us/davinci-pdex-plan-net/).
* CMS, "Interoperability and Patient Access Final Rule" (CMS-9115-F).
* CMS, "Interoperability and Prior Authorization Final Rule" (CMS-0057-F).

### 12.3 Companion documents in this repository

| Document | Role |
|----------|------|
| [README](README.md) | Identity and authority model |
| [GeneratingFederatedPayerIdentifiers.md](GeneratingFederatedPayerIdentifiers.md) | FPI derivation procedure |
| [WellKnownFileFormat.md](WellKnownFileFormat.md) | Annotated field-by-field format |
| [AllAtOnce.md](AllAtOnce.md) | Bulk provider directory publication |
| [FutureSteps.md](FutureSteps.md) | Deferred capabilities |
| [example_wellknown_payer_index.json](example_wellknown_payer_index.json) | Worked two-FPI example |
| [tools/FPI_maker_cli.py](tools/FPI_maker_cli.py) | Reference FPI generator |

### 12.4 Authors

This specification is maintained by the Federated Payer Identifier project. See
[COMMUNITY.md](COMMUNITY.md) for how to participate, and the repository's Git
history for individual contributions.

### 12.5 Notices

This specification is a "rough consensus and working code" prototype. It is not
a regulation, and publication here does not create an obligation on any payer.
Formats and processes may change as the National Provider and Payer Directory
evolves.

This work is dedicated to the public domain under
[Creative Commons CC0 1.0 Universal](LICENSE). To the extent possible under law,
the contributors have waived all copyright and related or neighboring rights to
this document.

This specification is provided on an "AS IS" basis. The authors and the
organizations they represent make no warranties, express or implied, including
any warranty that use of the information herein will not infringe any rights,
and the entire risk of implementing this specification is assumed by the
implementer.

HL7 and FHIR are registered trademarks of Health Level Seven International.
