# FPI Well-Known Index → NDH FHIR Mapping

This document specifies the translation layer between the
[Payer Well-Known Index JSON format](WellKnownFileFormat.md) and the three
HL7 FAST [NDH](https://build.fhir.org/ig/HL7/fhir-us-ndh/en/) profiles that
express the same facts as FHIR resources:

| Role | NDH profile | Canonical URL |
|------|-------------|---------------|
| Payer | NDH Organization Profile | `http://hl7.org/fhir/us/ndh/StructureDefinition/ndh-Organization` |
| Plan | NDH InsurancePlan Profile | `http://hl7.org/fhir/us/ndh/StructureDefinition/ndh-InsurancePlan` |
| Endpoint | NDH Endpoint Profile | `http://hl7.org/fhir/us/ndh/StructureDefinition/ndh-Endpoint` |
| Network (supporting) | NDH Network Profile | `http://hl7.org/fhir/us/ndh/StructureDefinition/ndh-Network` |

NDH element facts in this document were read from the NDH IG source
(`input/fsh/Base-Profiles.fsh`, `Base-Extensions.fsh`, `Base-Invariant.fsh`,
`Base-VS.fsh`) and the generated StructureDefinitions for version
**2.0.0-ballot**. Where this document says an element is Must Support, 1..1, or
bound to a value set, that is a statement about NDH, not about this prototype.

The central question this document answers is: **given a FHIR Bundle that is
supposed to carry the same information as a well-known index file, which fields
must be populated even though NDH leaves them optional?** Those obligations are
collected in the `Required for FPI bundle?` column of every mapping table, and
summarized in [Section 10](#10-ndh-requirements-fpi-cannot-fully-satisfy).

---

## 1. The compilation model

The well-known index file is a **normalized** representation. The FHIR Bundle is
a **denormalized** one. The two compression mechanisms that make the well-known
file small are exactly the two things FHIR cannot express:

1. **Endpoint cascade.** Endpoints may be declared once at the index scope and
   inherited by every plan in the document.
2. **Plan grouping.** Plans that share an endpoint set are collected into one
   `plan_group` so the endpoint set is written once rather than per plan.

FHIR has no cascade and no plan grouping. An `InsurancePlan` either references
an `Endpoint` or it does not. The translation layer is therefore a **compiler**:
it resolves the cascade, expands the groups, and emits explicit reference edges.

> The cascade is not an obstacle to the mapping. The cascade is the thing being
> compiled. A well-known file is the source form; the Bundle is the object form.

### 1.1 Resolution

For each plan *P* and each endpoint key *K*, in a single environment
(production resolves only against production; sandbox only against sandbox —
[EP-220](FederatedPayerIdentifierSpecification.md)):

```text
effective(P, K) =
    G[K]                 if K present in P's plan_group.plan_endpoints and G[K] != null
    ⊥  (suppressed)      if K present in P's plan_group.plan_endpoints and G[K] == null
    I[K]                 if K absent from the plan_group and present in index_endpoints
    ⊥  (no assertion)    otherwise

    where G = the plan_group's plan_endpoints, I = index_endpoints
```

The two `⊥` cases differ in authoring intent but are identical in the Bundle:
no reference is emitted. This is **not** a loss of information, because the
contrast is still visible in the output. A key suppressed with `null` in one
plan group while another group inherits it from the index produces a Bundle in
which one set of plans references the endpoint and another set does not. The
assertion "these plans are deliberately not served by that endpoint" survives
as the observable absence of an edge against the presence of sibling edges.


### 1.2 Deduplication

Emit **one `Endpoint` resource per distinct `(key, resolved URL, environment)`
triple**, not one per plan. Then reference that single resource from every
`InsurancePlan` whose resolution yielded it.

This matters at the scale the corpus actually exhibits: a plan group in the
seeded data may hold up to **330 plans**. Naively emitting per plan would
produce 330 identical `Endpoint` resources. The correct output is 1 `Endpoint`
and 330 references to it. The many-to-many relation that the cascade encodes
compactly becomes an explicit set of reference edges.

### 1.3 The two modes

| | **Mode A** — no plan data | **Mode B** — plan data present |
|---|---|---|
| Trigger | `plan_groups` is empty (EP-240) | `plan_groups` is non-empty |
| Endpoints attach to | `Organization.endpoint` | `InsurancePlan.endpoint`, on **every** plan |
| `InsurancePlan` emitted? | No | One per `plan_identifiers` entry |
| NDH note | `Organization.endpoint` **is** Must Support | `InsurancePlan.endpoint` is `0..*` and **not** Must Support |
| Status | Approximate. Attaching endpoints to the payer asserts less than the truth, but is an acceptable starting point when plans are unmodeled. | Target state |
| Corpus (788 files) | 4 files | 784 files |

In Mode B the defining property is that **an endpoint declared only at the index
scope still appears on every plan that inherits it**. The Bundle states the
payer's *effective* position. That a given edge arrived by inheritance rather
than by explicit declaration is a fact about the source file's compression, not
a fact about the payer's interoperability surface, and it is not represented.

Note the mild irony that the better-supported target element is the weaker one:
Mode A writes to a Must Support element, Mode B to one that is neither Must
Support nor required. Mode B is still correct, because it states the
plan-to-endpoint association that consumers actually need.

### 1.4 Mirroring rule (Mode B)

Index-scope endpoints MAY additionally be mirrored onto `Organization.endpoint`
— which is Must Support, and so is useful to populate — but **only for keys that
no plan group suppressed with `null`**.

Mirroring a suppressed key would resurrect, at the payer level, an endpoint the
payer explicitly declared does not serve some of its plans, defeating EP-210.
When a key is suppressed anywhere in the document, omit it from
`Organization.endpoint` and let the per-plan references carry the whole truth.

### 1.5 Determinism

Resource `id` values SHOULD be derived reproducibly, so that recompiling an
unchanged well-known file yields a byte-identical Bundle rather than fresh
random identifiers on each run. This mirrors the determinism discipline the
FPI itself already follows.

| Resource | Recommended `id` derivation |
|---|---|
| `Organization` (payer) | the FPI UUID |
| `InsurancePlan` | the `f_plan_id` UUID |
| `Endpoint` | UUIDv5 over `FPI + "\|" + endpoint key + "\|" + environment` |
| `Organization` (network) | UUIDv5 over `FPI + "\|network\|" + plan_group index` |

This is a recommendation of this mapping, not an NDH requirement.

---

## 2. Bundle inventory for the worked scenario

One payer, one plan group, all seven currently regulated payer endpoint types:

| # | Resource | Profile | Count | Source |
|---|---|---|---|---|
| 1 | `Organization` | `ndh-Organization` | 1 | the `is_fpi: true` identifier entry |
| 2 | `Organization` | `ndh-Network` | 1 | synthesized — see [Section 6](#6-networks) |
| 3 | `InsurancePlan` | `ndh-InsurancePlan` | 1 per plan | each `plan_identifiers` entry |
| 4 | `Endpoint` | `ndh-Endpoint` | 7 | resolved production endpoint keys |

`Bundle.type` is `collection` for a published snapshot, or `searchset` when the
Bundle is the response to a query against a FHIR server.

### 2.1 Legend

| Column | Meaning |
|---|---|
| **FPI field** | JSON path in the well-known index file |
| **NDH element** | FHIRPath into the profiled resource |
| **Card.** | NDH cardinality |
| **MS?** | Must Support in NDH |
| **Req?** | Required *for a conforming FPI bundle* — this mapping's obligation, which is often stricter than NDH |
| **Derivation** | How the value is produced |

A **Req? = Yes** against **MS? = no** is the interesting case: a field NDH
leaves optional that an FPI-derived Bundle must nonetheless carry.


---

## 3. Payer → `ndh-Organization`

Source: one `identifier` array entry with `is_fpi: true`. A file with several
FPI entries produces several `Organization` resources.

| FPI field | NDH element | Card. | MS? | Req? | Derivation |
|---|---|---|---|---|---|
| — | `meta.profile` | — | — | **Yes** | `.../ndh-Organization` |
| — | `meta.lastUpdated` | **1..1** | no | **Yes** | Git commit time of the well-known file, as UTC `instant` |
| `identifier[is_fpi].value` | `identifier:PIN.value` | **1..1** | **yes** | **Yes** | the FPI UUID |
| `identifier[is_fpi].system` | `identifier:PIN.system` | **1..1** | **yes** | **Yes** | `https://directory.cms.gov/payer_identification_system/fpi` |
| — | `identifier:PIN.type` | 1..1 | no | **Yes** | fixed `v2-0203#PAYERID` |
| `identifier[is_fpi==false]` | `identifier:PIN` (repeat) | 0..* | **yes** | **Yes** | one slice per crosswalk identifier (NAIC, CMS contract, state DOI) |
| `.expiration` | `identifier.period.end` | 0..1 | no | No | omit when `"current"`; otherwise the expiration date |
| `.expiration` | `identifier.extension:identifier-status` | 0..1 | no | No | `active` when `"current"` |
| `payerLegalName` | `name` | **1..1** | **yes** | **Yes** | verbatim |
| `payerContactWebsite` | `telecom[system=url].value` | 0..* | **yes** | **Yes** | `.system` = `url` |
| `payer_level_string_search_matches[]` | `alias[]` | 0..* | **yes** | **Yes** | one `alias` per string |
| — | `active` | **1..1** | **yes** | **Yes** | fixed `true` |
| — | `type` | **1..*** | **yes** | **Yes** | `organization-type#pay` (Payer) |
| resolved index endpoints | `endpoint[]` | 0..* | **yes** | Mode A | see [§1.4](#14-mirroring-rule-mode-b) |

### 3.1 Notes

**`type` must be `pay`, not `ins`.** `OrgTypeVS` is extensible over
`organization-type` and admits both `pay` (Payer) and `ins` (Insurance
Company). The FPI identity boundary is the entity holding insurance assets and
liability for a beneficiary set, and is the entity that operates the endpoints
— that is the payer role. `OrgTypeVS` explicitly **excludes** `ntwk`, which is
why networks are a separate profile ([Section 6](#6-networks)).

**Crosswalk identifiers all become `PIN` slices.** NDH slices
`Organization.identifier` on `type`, and every FPI payer identifier is a payer
identification number regardless of which authority issued it. The FPI itself
and its NAIC/contract/DOI crosswalks are therefore sibling `PIN` slices
distinguished by `system`. Consumers select the FPI by matching `system`.

**`fpi_source_system` / `fpi_source_value` have no NDH home.** See
[Section 9](#9-fpi-fields-with-no-ndh-home).


---

## 4. Plan → `ndh-InsurancePlan`

Source: one entry in `plan_groups[].plan_identifiers`. **One `InsurancePlan`
per plan, not per group.** The group is a compression device in the source
format and does not survive compilation.

| FPI field | NDH element | Card. | MS? | Req? | Derivation |
|---|---|---|---|---|---|
| — | `meta.profile` | — | — | **Yes** | `.../ndh-InsurancePlan` |
| — | `meta.lastUpdated` | **1..1** | no | **Yes** | Git commit time, UTC `instant` |
| `f_plan_id` | `identifier[0].value` | 0..* | **yes** | **Yes** | `.system` = `https://directory.cms.gov/payer_identification_system/federated_plan_id/plan/f_plan_id` |
| `system` + `value` | `identifier[1]` | 0..* | **yes** | **Yes** | the CMS contract/plan identifier, e.g. `H1234-432` |
| — | `status` | **1..1** | **yes** | **Yes** | fixed `active` |
| `line_of_business` (file level) | `type` | **1..1** | **yes** | **Yes** | see [§4.1](#41-line_of_business--insuranceplantype) |
| `plan_name` | `name` | 0..1 | **yes** | **Yes** | verbatim |
| `plan_level_string_search_matches[]` | `alias[]` | 0..* | no | **Yes** | one `alias` per string |
| `plan_group_string_search_match[]` | `alias[]` | 0..* | no | **Yes** | appended to every plan in the group |
| `parent_fpi` | `ownedBy` | 0..1 | no | **Yes** | `Organization/<FPI>` |
| `parent_fpi` | `administeredBy` | 0..1 | no | **Yes** | `Organization/<FPI>` — see note |
| `plan_website` | `contact.telecom[system=url].value` | 0..* | no | **Yes** | also appears as `plan_homepage#NNN` |
| resolved endpoints | `endpoint[]` | 0..* | **no** | **Yes (Mode B)** | the compiled set from [§1.1](#11-resolution) |
| — | `network` | 0..* | **yes** | **Yes** | [Section 6](#6-networks) |
| — | `coverageArea` | 0..* | **yes** | No | FPI carries no service area |

### 4.1 `line_of_business` → `InsurancePlan.type`

`line_of_business` is a **required file-level member** of the well-known format
(**WK-155**), introduced so that directory placement is derived rather than
load-bearing. A consumer can treat the corpus as a flat set of files and
recover the directory layout from the tag, instead of the reverse. The
permitted values, and the defaults in the table below, are enumerated in
[`reference_data/lines_of_business.json`](reference_data/lines_of_business.json)
as `default_fhir_product_type`.

`InsurancePlan.type` is `1..1` and extensibly bound to
`insurance-product-type`. Line of business is **coarser** than that value set,
so the mapping yields a defensible default, not a determination:

| `line_of_business` | Default `type` | Exact? |
|---|---|---|
| `medicare_advantage` | `mediadv` | No — `mediadvhmo` where the plan is an HMO |
| `medicaid_managed_care` | `medihmo` | No — `medi` for non-managed Medicaid |
| `healthcare_marketplace_plans` | `qhp` | Yes |
| `commercial_plans` | `commppo` | **No** — fans out to `commhmo`, `commepo`, `commpos`, `commhdhp` |
| `ERISA_plans` | *none* | **No** — self-funded ERISA has no clean code |
| `other` | *none* | No |

Where the default is not exact, the compiler SHOULD prefer a more specific code
if the plan name or source data supports it, and MUST record that the value was
inferred. `ERISA_plans` and `other` cannot satisfy a `1..1` required element
from LOB alone; those files need an explicit product type before they can
produce a conforming `InsurancePlan`. This is the single largest open data gap
in the mapping.

### 4.2 `ownedBy` vs `administeredBy`

FPI asserts one relationship — `parent_fpi`, the payer legal entity owning the
plan — so both elements receive the same reference. They diverge in reality
when a payer delegates administration to a TPA or vendor, which FPI does not
currently model. Setting both to the FPI is accurate for `ownedBy` and an
assumption for `administeredBy`; a compiler that can distinguish them should.


---

## 5. Endpoints → `ndh-Endpoint`

### 5.1 The seven currently regulated payer endpoint types

| # | Regulated type | FPI key(s) | `connectionType` | `ig-usecase` | IG |
|---|---|---|---|---|---|
| 1 | patient-to-payer | `carin_bluebutton_endpoint#1.0`, `davinci_pdex_patient_endpoint#2.0` | `hl7-fhir-rest` | `patientAccess` | CARIN BB / PDex |
| 2 | provider-to-payer general access | `davinci_pdex_provider_endpoint#1.1` | `hl7-fhir-rest` | `providerApi` | PDex |
| 3 | provider-directory | `davinci_pdex_provider_directory_endpoint#1.1` | `hl7-fhir-rest` | `provider-directory` | PDex Plan-Net |
| 3b | provider-directory (bulk) | `davinci_pdex_provider_directory_endpoint_all_at_once#1.1` | `rest-non-fhir` | `provider-directory` | PDex Plan-Net |
| 4 | prior-auth **CRD** | `davinci_crd_hook_endpoint#1.1` | **`cds-hooks-service`** | `coverage-requirements-discovery-crd` | Da Vinci CRD |
| 5 | prior-auth **DTR** | `davinci_dtr_qpackage_endpoint#1.2` | `hl7-fhir-rest` | `documentation-templates-rules-dtr` | Da Vinci DTR |
| 6 | prior-auth **PAS** | `davinci_pas_submission_endpoint#1.2` | `hl7-fhir-rest` | `pasOperation` | Da Vinci PAS |
| 7 | payer-to-payer | `davinci_pdex_payer_endpoint#1.1` | `hl7-fhir-rest` | `payerToPayer` | PDex |

`ig-usecase` codes come from `NdhImplementationGuideVS`, which unions
`NdhFhirEndpointUseCaseCS` (`patientAccess`, `pasOperation`, `payerToPayer`,
`providerApi`, `cdex`, `payerAttachment`) and
`NdhDirectTrustEndpointUsecaseCS` (which supplies `provider-directory`,
`coverage-requirements-discovery-crd`, `documentation-templates-rules-dtr`).

Additional FPI keys outside the seven regulated types map the same way:
`davinci_cdex_attachsubmit_endpoint#2.1` → `cdex`;
`davinci_pdex_formulary_endpoint#2.0` → `formulary`;
`carin_rtpbc_member_endpoint#1.0` / `carin_rtpbc_provider_endpoint#1.0` →
`prescriptions`; `uv_smart_scheduling_links_endpoint` → `scheduling`;
`tic_table_of_contents#issuer-NNNNN` and
`cms_provider_directory_machine_readable_format_endpoint` →
`rest-non-fhir` with `item-service-price-transparency` and
`provider-directory` respectively.

### 5.2 Per-endpoint element map

Applies to each of the seven resources.

| FPI field | NDH element | Card. | MS? | Req? | Derivation |
|---|---|---|---|---|---|
| — | `meta.profile` | — | — | **Yes** | `.../ndh-Endpoint` |
| — | `meta.lastUpdated` | **1..1** | no | **Yes** | Git commit time, UTC `instant` |
| the key's value (URL) | `address` | **1..1** | no | **Yes** | the resolved absolute URL — the routing field |
| — | `status` | **1..1** | **yes** | **Yes** | fixed `active` |
| key family | `connectionType` | **1..1** | **yes** | **Yes** | per [§5.1](#51-the-seven-currently-regulated-payer-endpoint-types) |
| — | `payloadType` | **1..1** | no | **Yes** | `data-absent-reason#not-applicable` — NDH narrows `0..*`→`1..1`; binding is extensible, see [§5.3](#53-payloadmimetype-is-fhir-only) |
| — | `payloadMimeType` | 0..* | **yes** | Conditional | `application/fhir+json`; **omit for non-FHIR endpoints** — see [§5.3](#53-payloadmimetype-is-fhir-only) |
| — | `name` | 0..1 | **yes** | **Yes** | synthesized, e.g. `"<payerLegalName> — Da Vinci PAS Submission"` |
| the FPI | `managingOrganization` | 0..1 | **yes** | **Yes** | `Organization/<FPI>` — the payer |
| — | `identifier` | 0..* | **yes** | SHOULD | deterministic, per [§1.5](#15-determinism) |
| `ndh_meta_fhir_signup_url` | `contact:configuration-url.value` | 0..* | **yes** | **Yes** (EP-100) | `.system` fixed `url` |
| environment | `extension:environmentType` | 0..* | no | **Yes** | `prod` from `plan_endpoints`; `test` from `plan_endpoints_sandbox` |
| `#version` suffix | `extension:implementation-guide` | 0..* | no | **Yes** | see [§5.4](#54-version-suffixes--the-implementation-guide-extension) |


### 5.3 `payloadMimeType` is FHIR-only

`payloadMimeType` is bound **required** to `EndpointFhirMimeTypeVS`, which
contains exactly `application/fhir+xml`, `application/fhir+json`, and
`application/fhir+turtle`. A required binding admits no other code.

Consequently, endpoints that are not FHIR REST **must omit `payloadMimeType`
entirely** rather than state their true media type:

| Endpoint | True media type | Action |
|---|---|---|
| CRD (`cds-hooks-service`) | `application/json` (CDS Hooks) | **omit** |
| Provider directory bulk (`all_at_once`) | `application/zip`, NDJSON | **omit** |
| TiC table of contents | `application/json` | **omit** |
| CMS machine-readable directory | `application/json` | **omit** |

Omitting is legal — the element is `0..*`. But a Must Support element goes
unpopulated for four endpoint families, and the Bundle cannot state the media
type a client should actually expect. This is an NDH modeling limitation, not
an FPI one, and is recorded in [Section 10](#10-ndh-requirements-fpi-cannot-fully-satisfy).

`payloadType` is a related but milder case. NDH narrows it to `1..1`, and
`EndpointPayloadTypeVS` contains the single code `not-applicable`. The binding
is **extensible** rather than required, so a more descriptive code from another
system is permitted where one genuinely applies. Absent such a code in the FPI
source, emit `not-applicable` — satisfying the required element without
asserting anything false.

### 5.4 Version suffixes → the `implementation-guide` extension

An FPI key of the form `family#1.2` encodes the **protocol** version (EP-060).
That decomposes into `base-ext-implementation-guide` sub-extensions:

| Sub-extension | Value | Source |
|---|---|---|
| `ig-uri` (canonical) | e.g. `https://hl7.org/fhir/us/davinci-pas/` | `ig_url` in [`reference_data/endpoint_types.json`](reference_data/endpoint_types.json) |
| `ig-version` (string) | e.g. `1.2` | the `#` suffix |
| `ig-usecase` (CodeableConcept) | e.g. `pasOperation` | [§5.1](#51-the-seven-currently-regulated-payer-endpoint-types) |
| `ig-name` (string) | e.g. `Da Vinci PAS` | derived from the IG |

A profile coordinate such as `carin_bluebutton_endpoint#1.0_uscore3.1` carries
a second axis — the US Core version. Record it as an additional `ig-option`,
and note that two keys differing only by profile coordinate resolve to two
distinct `Endpoint` resources under [§1.2](#12-deduplication) when their URLs
differ, as they do in the worked example.

### 5.5 Sandbox

`plan_endpoints_sandbox` compiles to `Endpoint` resources identical in shape to
production ones but carrying `environmentType = test`.

`NdhEndpointEnvironmentCS` offers `prod`, `staging`, `dev`, `test`, `train` —
there is **no `sandbox` code**. This mapping adopts `test` as the agreed
representation of "anything that is not production," consistent with EP-170
treating `sandbox` as the single non-production spelling.

Sandbox endpoints MUST NOT be referenced from an `InsurancePlan` in a way that
makes them indistinguishable from production ones. The `environmentType`
extension is the only thing preventing a consumer from routing live traffic to
a test system, so it is required, not optional, on every sandbox `Endpoint`.
Because an extension is easy to overlook, a conservative consumer that cannot
read `environmentType` should treat the Bundle as production-only and ignore
any endpoint it cannot positively confirm. Compilers MAY instead emit
production and sandbox as two separate Bundles.


---

## 6. Networks

FPI **does** have a network concept. It is expressed indirectly: the networks
belonging to a plan are whatever the provider directory behind
`davinci_pdex_provider_directory_endpoint` says they are. The well-known file
does not enumerate networks because the provider-directory endpoint is the
authority for them.

NDH requires that a network be named. The `ndh-InsurancePlan` invariant
**`network-or-NatlDirwork`** is severity **error**:

```text
network.exists() or coverage.network.exists() or plan.network.exists()
```

So an `InsurancePlan` with no network reference is invalid, and the network
identity is not in the source file.

### 6.1 Adopted approach — a Network that points at its own authority

Emit one `ndh-Network` Organization per plan group, whose `Organization.endpoint`
references that group's provider-directory `Endpoint`. The Bundle is then valid
standalone, and a consumer that wants real network membership follows the
endpoint to the Plan-Net server — which is exactly where FPI says the answer
lives.

| NDH element | Card. | MS? | Value |
|---|---|---|---|
| `meta.profile` | — | — | `.../ndh-Network` |
| `meta.lastUpdated` | **1..1** | no | Git commit time |
| `active` | **1..1** | **yes** | fixed `true` |
| `type` | **1..1** | **yes** | `organization-type#ntwk` (**required** binding to `NetworkTypeVS`) |
| `name` | **1..1** | **yes** | derived, e.g. `"<payerLegalName> Provider Network"` |
| `partOf` | 0..1 | no | `Organization/<FPI>` |
| `endpoint` | 0..* | **yes** | the provider-directory `Endpoint` — **the authority for membership** |

`InsurancePlan.network` then references this resource.

This resource is **synthesized by the compiler and is not authored data**. It
asserts only that a network exists and where to resolve it. It must not be read
as an enumeration of network membership, and round-tripping back to FPI
discards it ([Section 12](#12-round-trip-notes)).

Where a plan group publishes no provider-directory endpoint, the Network stub
has no authority to point at. Emit it with `name` and `type` only, or accept
that the `InsurancePlan` cannot satisfy `network-or-NatlDirwork`.

### 6.2 Alternatives considered

| Option | Description | Why not adopted |
|---|---|---|
| **(a)** External reference | `InsurancePlan.network` → an absolute URL into the payer's live Plan-Net server | Truest to the model, but the reference is unresolvable within the Bundle and FPI carries no network ids to construct it |
| **(c)** Both | Stub in-Bundle carrying the Plan-Net URL as an `identifier` | Strictly better than (b) once network ids exist upstream; adopt when FPI or Plan-Net supplies a stable network identifier |

Option (c) is the likely end state. It is not adopted now only because there is
no network identifier in the source data to put in the `identifier` element.

---

## 7. URLs that are not endpoints

Four FPI keys are URLs that are **not** interoperability endpoints. Modeling
them as `Endpoint` resources would be wrong: an `ndh-Endpoint` asserts
`status = active`, a `connectionType`, a `payloadType`, and a machine-callable
`address`. A documentation page has none of those, and a client that treated it
as an endpoint would try to call it as an API.

| FPI key | What it is | NDH target |
|---|---|---|
| `ndh_meta_fhir_signup_url` | where a developer registers for access (EP-100) | `Endpoint.contact:configuration-url` on each endpoint it governs |
| `ndh_meta_documentation_url` | developer documentation (EP-110) | `Organization.telecom[system=url]` |
| `payer_homepage` | payer marketing site | `Organization.telecom[system=url]` |
| `plan_homepage#NNN` | per-plan marketing page | `InsurancePlan.contact.telecom[system=url]` on the matching plan |

`ndh_meta_fhir_signup_url` is the one that lands inside `Endpoint`, because NDH
defines the `configuration-url` contact slice as precisely *"Website where
developers can configure access to this endpoint"*, with `.system` fixed to
`url` and both `.system` and `.value` at `1..1`. That is an exact semantic
match for EP-100.

Distinguishing `plan_homepage#NNN` requires matching the `#NNN` suffix against
the plan portion of the CMS contract/plan identifier (`H1234-432` → `#432`).

---

## 8. Resolved worked mapping — Mode B

Using the first plan group of
[`example_wellknown_payer_index.json`](example_wellknown_payer_index.json):
three plans (`H1234-432`, `H1234-433`, `H1234-434`) sharing one endpoint set.

Compiled output:

| Resource | Count | Note |
|---|---|---|
| `Organization` (payer) | 1 | FPI `13e068e1-cd54-5baa-b7e3-79761afe7afc` |
| `Organization` (network) | 1 | points at the provider-directory endpoint |
| `InsurancePlan` | **3** | one per plan, **not** one per group |
| `Endpoint` (production) | **17** | 14 explicit group keys + 3 inherited from `index_endpoints` |
| `Endpoint` (sandbox) | **6** | 5 explicit + 1 inherited; `environmentType = test` |

Each of the three `InsurancePlan` resources references **the same 17
production `Endpoint` resources**. The group existed only to avoid writing the
endpoint set three times; after compilation it has no representation.

Those 17 endpoints resolve to only **14 distinct URLs**, because some keys
share an address — `carin_bluebutton_endpoint#1.0`,
`davinci_pdex_patient_endpoint#2.0`, and
`davinci_pdex_formulary_endpoint#2.0` all point at
`https://example.org/fhir/v3/patientaccess/`. They remain **three separate
`Endpoint` resources**, because each carries a different `ig-usecase` and
asserts a different capability at that address. This is why
[§1.2](#12-deduplication) keys deduplication on the
`(key, URL, environment)` triple and not on the URL alone.

Note the `index_endpoints` inheritance in that file:
`davinci_cdex_attachsubmit_endpoint#2.1`,
`carin_rtpbc_member_endpoint#1.0`, and `carin_rtpbc_provider_endpoint#1.0` are
declared **only** at the index scope, yet all three plans reference them,
because no plan group overrides them.

The second plan group in the same file demonstrates suppression: it sets
`carin_rtpbc_member_endpoint#1.0` and `carin_rtpbc_provider_endpoint#1.0` to
`null`. Its plans therefore **do not** reference those endpoints, while the
first group's plans do. The suppression is visible in the compiled Bundle as
the contrast between the two plan sets — which is why [§1.1](#11-resolution)
holds that nothing is lost.

Because those two keys are suppressed somewhere in the document,
[§1.4](#14-mirroring-rule-mode-b) forbids mirroring them onto
`Organization.endpoint`.

---

## 9. FPI fields with no NDH home

| FPI field | Purpose | Disposition |
|---|---|---|
| `copied_from_url` | provenance of the working copy (WK-140) | Not mapped. Could become `Bundle.meta.source`. |
| `is_seeded` | seeded vs. curated lifecycle (WK-150) | Not mapped. A repository workflow detail, not payer data. Could become a `meta.tag`. |
| `resourceType` | the FHIR-ish type marker | Dropped — superseded by real `meta.profile` values |
| `fpi_source_system` | which identifier system anchored the FPI (FPI-100) | **No home.** See below. |
| `fpi_source_value` | the value hashed to produce the FPI (FPI-100) | **No home.** See below. |
| `notes` | free text on a crosswalk identifier | Not mapped |
| `expiration` | `"current"` or a date | Partially — `identifier.period.end` + `identifier-status` |
| `parent_fpi` on plan identifiers | owning payer entity | Mapped via `ownedBy` / `administeredBy` |
| `is_fpi` | marks the FPI entry | Implicit in `identifier.system` |

### 9.1 The `fpi_source_*` gap

These two fields are what make an FPI **verifiable**: FPI-130 requires that the
UUID recompute from its declared source. Dropping them means a consumer holding
only the FHIR Bundle cannot verify that the FPI is well-formed — it must return
to the well-known file.

There is no natural NDH element for "this identifier was derived from that
one." Options, none yet adopted:

* a new extension on `Organization.identifier:PIN` carrying system and value;
* `Identifier.assigner` — semantically wrong, as the assigner is an
  organization, not a source identifier;
* accept the loss and treat the well-known file as the system of record for
  FPI provenance, with the Bundle as a derived projection.

The third is the current de facto position and is consistent with this
repository being the trusted working copy.

---

## 10. NDH requirements FPI cannot fully satisfy

| # | Issue | Severity | Resolution |
|---|---|---|---|
| 1 | `InsurancePlan.type` is `1..1`; `line_of_business` is coarser, and `ERISA_plans` / `other` have no code | **Blocking** for those LOBs | [§4.1](#41-line_of_business--insuranceplantype). Needs explicit product type in source. |
| 2 | `network-or-NatlDirwork` is an **error**-severity invariant; FPI names no network | **Blocking** | Synthesized Network stub, [§6.1](#61-adopted-approach--a-network-that-points-at-its-own-authority) |
| 3 | `payloadMimeType` required-bound to FHIR media types only | Medium | Omit for non-FHIR endpoints, [§5.3](#53-payloadmimetype-is-fhir-only) |
| 4 | `payloadType` is `1..1` but its value set contains only `not-applicable` (extensible, so other codes are allowed) | Low | Emit `not-applicable` absent a better code |
| 5 | `Endpoint.name` is MS; FPI has no endpoint names | Low | Synthesize from payer name + endpoint family |
| 6 | No `sandbox` code in `NdhEndpointEnvironmentCS` | Low | Use `test`, [§5.5](#55-sandbox) |
| 7 | `fpi_source_system` / `fpi_source_value` unrepresentable | Medium | [§9.1](#91-the-fpi_source_-gap) |
| 8 | `InsurancePlan.coverageArea` is MS; FPI has no service area | Low | Omit |
| 9 | `Organization.address` is MS; FPI carries no payer address | Low | Omit — FPI deliberately holds a contact *website*, not a postal address |
| 10 | `meta.lastUpdated` is `1..1` on all three profiles | Resolved | Git commit time of the well-known file |

Items 3, 4, and 6 are limitations of NDH rather than of FPI, and are candidates
for NDH ballot comments rather than changes to this format.

---

## 11. Validation

A compiled Bundle should be validated against the NDH profiles before
publication:

```bash
java -jar validator_cli.jar bundle.json \
  -version 4.0.1 \
  -ig hl7.fhir.us.ndh#current \
  -profile http://hl7.org/fhir/us/ndh/StructureDefinition/ndh-Organization
```

Expect Must Support informational notices for the elements listed in
[Section 10](#10-ndh-requirements-fpi-cannot-fully-satisfy). Errors on
`network-or-NatlDirwork` or on a missing `InsurancePlan.type` indicate the
compiler skipped [§6.1](#61-adopted-approach--a-network-that-points-at-its-own-authority)
or [§4.1](#41-line_of_business--insuranceplantype).


---

## 12. Round-trip notes

Compilation is **lossy in one direction and recoverable in the other**.

**FHIR → FPI (decompilation).** Plan groups are recoverable: group the
`InsurancePlan` resources by their set of referenced `Endpoint` resources, and
each distinct set is a plan group. What is *not* recoverable is the
index-versus-group split. If every plan references an endpoint, the decompiler
cannot tell whether the payer declared it once at the index scope or repeated
it in each group. Decompilation produces a semantically equivalent file, not a
byte-identical one.

**Lost entirely in the round trip:**

* `copied_from_url`, `is_seeded`, `notes`, `fpi_source_system`, `fpi_source_value`
* the index-vs-plan-group authoring choice
* the distinction between a `null`-suppressed key and a never-mentioned one,
  *for an individual plan considered alone* — though as
  [§1.1](#11-resolution) notes, the contrast between sibling plan sets survives

**Added by compilation, not present in the source:**

* the synthesized `ndh-Network` Organization ([§6](#6-networks))
* synthesized `Endpoint.name` values
* `InsurancePlan.type`, where inferred from `line_of_business`

A decompiler must discard these rather than treat them as payer assertions.

---

## 13. Open questions

1. **Network identity.** Adopt option (c) from
   [§6.2](#62-alternatives-considered) once a stable network identifier exists
   upstream, so the stub can carry a resolvable Plan-Net reference.
2. **Product type.** `InsurancePlan.type` cannot be derived from
   `line_of_business` for `ERISA_plans` and `other`. Either add an explicit
   per-plan product type to the well-known format, or document those lines of
   business as unable to produce conforming `InsurancePlan` resources.
3. **FPI provenance.** Whether to propose an NDH extension carrying
   `fpi_source_system` / `fpi_source_value`, or to accept the well-known file
   as the system of record ([§9.1](#91-the-fpi_source_-gap)).
4. **Bundle vs. server.** This document describes a `collection` Bundle. The
   same mapping applies to a `searchset` response, but a server implementation
   additionally needs the NDH search parameters (`Endpoint:organization`,
   `InsurancePlan:endpoint`, `InsurancePlan:owned-by`) wired to the compiled
   references.
5. ~~**`line_of_business` enumeration.**~~ **Resolved.** The values are
   enumerated in
   [`reference_data/lines_of_business.json`](reference_data/lines_of_business.json)
   and required by WK-155. Each entry carries `default_fhir_product_type`, so
   the mapping in [§4.1](#41-line_of_business--insuranceplantype) is
   data-driven rather than hardcoded in prose.

---

## References

| Resource | Location |
|---|---|
| Well-known format | [WellKnownFileFormat.md](WellKnownFileFormat.md) |
| Normative rules | [FederatedPayerIdentifierSpecification.md](FederatedPayerIdentifierSpecification.md) |
| Endpoint families | [reference_data/endpoint_types.json](reference_data/endpoint_types.json) |
| Plan identifier systems | [reference_data/current_plan_identification_systems.json](reference_data/current_plan_identification_systems.json) |
| Payer identifier systems | [reference_data/current_payer_identification_systems.json](reference_data/current_payer_identification_systems.json) |
| Lines of business | [reference_data/lines_of_business.json](reference_data/lines_of_business.json) |
| Example index file | [example_wellknown_payer_index.json](example_wellknown_payer_index.json) |
| NDH IG | https://build.fhir.org/ig/HL7/fhir-us-ndh/en/ |
| NDH Organization | https://build.fhir.org/ig/HL7/fhir-us-ndh/en/StructureDefinition-ndh-Organization.html |
| NDH InsurancePlan | https://build.fhir.org/ig/HL7/fhir-us-ndh/en/StructureDefinition-ndh-InsurancePlan.html |
| NDH Endpoint | https://build.fhir.org/ig/HL7/fhir-us-ndh/en/StructureDefinition-ndh-Endpoint.html |
| NDH Network | https://build.fhir.org/ig/HL7/fhir-us-ndh/en/StructureDefinition-ndh-Network.html |

