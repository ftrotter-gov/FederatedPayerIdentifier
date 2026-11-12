# FPI Well-Known → NDH FHIR Column Crosswalk

A field-level crosswalk: **every value carried in a payer well-known index
file, and the NDH FHIR element it maps to.** Nothing else.

This document is deliberately narrow. It answers "where does this JSON value
go?" and omits the compilation model, the two publication modes, endpoint
resolution, synthesized Network resources, round-tripping, and the gap
analysis. Those live in
[FPI_WellKnown_To_NDH_FHIR_Map.md](FPI_WellKnown_To_NDH_FHIR_Map.md), which is
the normative companion and should be read first for *why* the mapping takes
this shape.

NDH element facts are from the NDH IG at version **2.0.0-ballot**.

## Legend

| Column | Meaning |
|---|---|
| **FPI field** | JSON path in the well-known index file |
| **NDH element** | FHIRPath into the profiled resource |
| **Card.** | NDH cardinality |
| **MS?** | Must Support in NDH |
| **Req?** | Required *for a conforming FPI bundle* — often stricter than NDH |
| **Derivation** | How the value is produced |

A **Req? = Yes** against **MS? = no** marks a field NDH leaves optional that an
FPI-derived bundle must nonetheless carry.

---

## 1. Payer values → `ndh-Organization`

Source: each `identifier` array entry with `is_fpi: true`. A file with several
FPI entries produces several `Organization` resources.

| FPI field | NDH element | Card. | MS? | Req? | Derivation |
|---|---|---|---|---|---|
| `identifier[is_fpi].value` | `identifier:PIN.value` | **1..1** | **yes** | **Yes** | the FPI UUID |
| `identifier[is_fpi].system` | `identifier:PIN.system` | **1..1** | **yes** | **Yes** | `https://directory.cms.gov/payer_identification_system/fpi` |
| `identifier[is_fpi==false]` | `identifier:PIN` (repeat) | 0..* | **yes** | **Yes** | one slice per crosswalk identifier (NAIC, CMS contract, state DOI) |
| `identifier[].expiration` | `identifier.period.end` | 0..1 | no | No | omit when `"current"`; otherwise the expiration date |
| `identifier[].expiration` | `identifier.extension:identifier-status` | 0..1 | no | No | `active` when `"current"` |
| `payerLegalName` | `name` | **1..1** | **yes** | **Yes** | verbatim |
| `payerContactWebsite` | `telecom[system=url].value` | 0..* | **yes** | **Yes** | `.system` = `url` |
| `payer_level_string_search_matches[]` | `alias[]` | 0..* | **yes** | **Yes** | one `alias` per string |
| `ndh_meta_documentation_url` | `telecom[system=url].value` | 0..* | **yes** | **Yes** (EP-110) | developer documentation; a web page, not a callable endpoint |
| `payer_homepage` | `telecom[system=url].value` | 0..* | **yes** | No | payer marketing site |
| resolved index endpoints | `endpoint[]` | 0..* | **yes** | Mode A | mirrored only for keys no plan group suppressed |

**Constants** — required by NDH, with no well-known source:
`meta.profile` = `.../ndh-Organization`;
`meta.lastUpdated` = Git commit time of the file (UTC `instant`, **1..1**);
`active` = `true` (**1..1**);
`type` = `organization-type#pay` (**1..\***);
`identifier:PIN.type` = `v2-0203#PAYERID`.



---

## 2. Plan values → `ndh-InsurancePlan`

Source: each entry in `plan_groups[].plan_identifiers`. **One `InsurancePlan`
per plan, not per group** — the group is a compression device in the source
format and does not survive into FHIR.

| FPI field | NDH element | Card. | MS? | Req? | Derivation |
|---|---|---|---|---|---|
| `f_plan_id` | `identifier[0].value` | 0..* | **yes** | **Yes** | `.system` = `https://directory.cms.gov/payer_identification_system/federated_plan_id/plan/f_plan_id` |
| `system` + `value` | `identifier[1]` | 0..* | **yes** | **Yes** | the CMS contract/plan identifier, e.g. `H1234-432` |
| `line_of_business` (file level) | `type` | **1..1** | **yes** | **Yes** | see [§2.1](#21-line_of_business--insuranceplantype) |
| `plan_name` | `name` | 0..1 | **yes** | **Yes** | verbatim |
| `plan_level_string_search_matches[]` | `alias[]` | 0..* | no | **Yes** | one `alias` per string |
| `plan_group_string_search_match[]` | `alias[]` | 0..* | no | **Yes** | appended to every plan in the group |
| `parent_fpi` | `ownedBy` | 0..1 | no | **Yes** | `Organization/<FPI>` |
| `parent_fpi` | `administeredBy` | 0..1 | no | **Yes** | `Organization/<FPI>` |
| `plan_website` | `contact.telecom[system=url].value` | 0..* | no | **Yes** | the plan's own page |
| `plan_homepage#NNN` | `contact.telecom[system=url].value` | 0..* | no | No | match `#NNN` against the plan portion of the CMS identifier (`H1234-432` → `#432`) |
| resolved endpoints | `endpoint[]` | 0..* | **no** | **Yes (Mode B)** | the compiled per-plan set |

**Constants:** `meta.profile` = `.../ndh-InsurancePlan`;
`meta.lastUpdated` = Git commit time (**1..1**); `status` = `active` (**1..1**).


### 2.1 `line_of_business` → `InsurancePlan.type`

`line_of_business` is a **required file-level member** (**WK-155**). Permitted
values and the defaults below are enumerated in
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
from line of business alone; those files need an explicit product type before
they can produce a conforming `InsurancePlan`.


---

## 3. Endpoint values → `ndh-Endpoint`

Source: each resolved key/value pair in `plan_endpoints`,
`plan_endpoints_sandbox`, `index_endpoints`, and `index_endpoints_sandbox`.

One `Endpoint` resource per distinct `(key, resolved URL, environment)` triple.
Keys whose value is `null` produce no resource.

| FPI field | NDH element | Card. | MS? | Req? | Derivation |
|---|---|---|---|---|---|
| the key's value (URL) | `address` | **1..1** | no | **Yes** | the resolved absolute URL — the routing field |
| key family | `connectionType` | **1..1** | **yes** | **Yes** | `hl7-fhir-rest` for FHIR REST; `cds-hooks-service` for CRD; `rest-non-fhir` for bulk/TiC/CMS machine-readable |
| key family | `extension:implementation-guide.ig-usecase` | 0..* | no | **Yes** | see [§3.3](#33-version-suffixes--the-implementation-guide-extension) |
| `#version` suffix | `extension:implementation-guide` | 0..* | no | **Yes** | see [§3.3](#33-version-suffixes--the-implementation-guide-extension) |
| which object the key came from | `extension:environmentType` | 0..* | no | **Yes** | `prod` from `plan_endpoints`; `test` from `plan_endpoints_sandbox` |
| `ndh_meta_fhir_signup_url` | `contact:configuration-url.value` | 0..* | **yes** | **Yes** (EP-100) | `.system` fixed `url`; applied to each endpoint it governs |
| the owning FPI | `managingOrganization` | 0..1 | **yes** | **Yes** | `Organization/<FPI>` — the payer |
| — | `name` | 0..1 | **yes** | **Yes** | synthesized, e.g. `"<payerLegalName> — Da Vinci PAS Submission"` |
| — | `identifier` | 0..* | **yes** | SHOULD | deterministic, so recompiling is stable |
| — | `payloadMimeType` | 0..* | **yes** | Conditional | `application/fhir+json`; **omit for non-FHIR endpoints** — see [§3.2](#32-payloadmimetype-is-fhir-only) |

**Constants:** `meta.profile` = `.../ndh-Endpoint`;
`meta.lastUpdated` = Git commit time (**1..1**); `status` = `active` (**1..1**);
`payloadType` = `data-absent-reason#not-applicable` (**1..1**).

`ndh_meta_fhir_signup_url` is the only non-API URL that lands inside
`Endpoint`, because NDH defines the `configuration-url` contact slice as
precisely *"Website where developers can configure access to this endpoint"*,
with `.system` fixed to `url` and both `.system` and `.value` at `1..1`. That
is an exact semantic match for EP-100. The other metadata URLs
(`ndh_meta_documentation_url`, `payer_homepage`, `plan_homepage#NNN`) are web
pages rather than callable services and map to `telecom` on the payer or plan —
see [§1](#1-payer-values--ndh-organization) and
[§2](#2-plan-values--ndh-insuranceplan).

### 3.1 Endpoint family → `connectionType` and `ig-usecase`

| FPI key | `connectionType` | `ig-usecase` |
|---|---|---|
| `carin_bluebutton_endpoint#1.0` | `hl7-fhir-rest` | `patientAccess` |
| `davinci_pdex_patient_endpoint#2.0` | `hl7-fhir-rest` | `patientAccess` |
| `davinci_pdex_provider_endpoint#1.1` | `hl7-fhir-rest` | `providerApi` |
| `davinci_pdex_provider_directory_endpoint#1.1` | `hl7-fhir-rest` | `provider-directory` |
| `davinci_pdex_provider_directory_endpoint_all_at_once#1.1` | `rest-non-fhir` | `provider-directory` |
| `davinci_crd_hook_endpoint#1.1` | `cds-hooks-service` | `coverage-requirements-discovery-crd` |
| `davinci_dtr_qpackage_endpoint#1.2` | `hl7-fhir-rest` | `documentation-templates-rules-dtr` |
| `davinci_pas_submission_endpoint#1.2` | `hl7-fhir-rest` | `pasOperation` |
| `davinci_pdex_payer_endpoint#1.1` | `hl7-fhir-rest` | `payerToPayer` |
| `davinci_cdex_attachsubmit_endpoint#2.1` | `hl7-fhir-rest` | `cdex` |
| `davinci_pdex_formulary_endpoint#2.0` | `hl7-fhir-rest` | `formulary` |
| `carin_rtpbc_member_endpoint#1.0` | `hl7-fhir-rest` | `prescriptions` |
| `carin_rtpbc_provider_endpoint#1.0` | `hl7-fhir-rest` | `prescriptions` |
| `uv_smart_scheduling_links_endpoint` | `hl7-fhir-rest` | `scheduling` |
| `cms_provider_directory_machine_readable_format_endpoint` | `rest-non-fhir` | `provider-directory` |
| `tic_table_of_contents#issuer-NNNNN` | `rest-non-fhir` | `item-service-price-transparency` |

`ig-usecase` codes come from `NdhImplementationGuideVS`, which unions
`NdhFhirEndpointUseCaseCS` and `NdhDirectTrustEndpointUsecaseCS`.

### 3.2 `payloadMimeType` is FHIR-only

`payloadMimeType` is bound **required** to `EndpointFhirMimeTypeVS`, which
contains exactly `application/fhir+xml`, `application/fhir+json`, and
`application/fhir+turtle`. A required binding admits no other code.

Endpoints that are not FHIR REST **must omit `payloadMimeType` entirely**
rather than state their true media type:

| Endpoint | True media type | Action |
|---|---|---|
| CRD (`cds-hooks-service`) | `application/json` (CDS Hooks) | **omit** |
| Provider directory bulk (`all_at_once`) | `application/zip`, NDJSON | **omit** |
| TiC table of contents | `application/json` | **omit** |
| CMS machine-readable directory | `application/json` | **omit** |

Omitting is legal — the element is `0..*`. But a Must Support element goes
unpopulated for four endpoint families, and the bundle cannot state the media
type a client should expect. This is an NDH modeling limitation, not an FPI
one.

`payloadType` is a milder case. NDH narrows it to `1..1`, and
`EndpointPayloadTypeVS` contains the single code `not-applicable`. The binding
is **extensible** rather than required, so a more descriptive code from another
system is permitted where one genuinely applies. Absent such a code in the FPI
source, emit `not-applicable`.


### 3.3 Version suffixes → the `implementation-guide` extension

An FPI key of the form `family#1.2` encodes the **protocol** version (EP-060).
That decomposes into `base-ext-implementation-guide` sub-extensions:

| Sub-extension | Value | Source |
|---|---|---|
| `ig-uri` (canonical) | e.g. `https://hl7.org/fhir/us/davinci-pas/` | `ig_url` in [`reference_data/endpoint_types.json`](reference_data/endpoint_types.json) |
| `ig-version` (string) | e.g. `1.2` | the `#` suffix |
| `ig-usecase` (CodeableConcept) | e.g. `pasOperation` | [§3.1](#31-endpoint-family--connectiontype-and-ig-usecase) |
| `ig-name` (string) | e.g. `Da Vinci PAS` | derived from the IG |
| profile coordinate | `ig-option` | the trailing `_uscore3.1` form, where present |

A profile coordinate such as `carin_bluebutton_endpoint#1.0_uscore3.1` carries
a second axis — the US Core version — recorded as an additional `ig-option`.
Two keys differing only by profile coordinate produce two distinct `Endpoint`
resources when their URLs differ.

### 3.4 Sandbox

`plan_endpoints_sandbox` and `index_endpoints_sandbox` compile to `Endpoint`
resources identical in shape to production ones but carrying
`environmentType = test`.

`NdhEndpointEnvironmentCS` offers `prod`, `staging`, `dev`, `test`, `train` —
there is **no `sandbox` code**. This mapping adopts `test` as the
representation of "anything that is not production," consistent with EP-170
treating `sandbox` as the single non-production spelling.

The `environmentType` extension is the only thing preventing a consumer from
routing live traffic to a test system, so it is required, not optional, on
every sandbox `Endpoint`. Because an extension is easy to overlook, a
conservative consumer that cannot read `environmentType` should treat the
bundle as production-only and ignore any endpoint it cannot positively
confirm. Compilers MAY instead emit production and sandbox as two separate
bundles.

---

## 4. File-level values

| FPI field | NDH element | Req? | Derivation |
|---|---|---|---|
| `line_of_business` | `InsurancePlan.type` | **Yes** | [§2.1](#21-line_of_business--insuranceplantype) |
| *(Git commit time)* | `meta.lastUpdated` on every resource | **Yes** | not a JSON member; taken from Git history |
| `index_endpoints` | `Endpoint` resources + `InsurancePlan.endpoint` refs | **Yes** | inherited by every plan that does not override the key |
| `index_endpoints_sandbox` | as above, `environmentType = test` | **Yes** | resolves only against `plan_endpoints_sandbox` |

---


## References

| Resource | Location |
|---|---|
| Full mapping and compilation model | [FPI_WellKnown_To_NDH_FHIR_Map.md](FPI_WellKnown_To_NDH_FHIR_Map.md) |
| Well-known format | [WellKnownFileFormat.md](WellKnownFileFormat.md) |
| Normative rules | [FederatedPayerIdentifierSpecification.md](FederatedPayerIdentifierSpecification.md) |
| Endpoint families | [reference_data/endpoint_types.json](reference_data/endpoint_types.json) |
| Lines of business | [reference_data/lines_of_business.json](reference_data/lines_of_business.json) |
| NDH Organization | https://build.fhir.org/ig/HL7/fhir-us-ndh/en/StructureDefinition-ndh-Organization.html |
| NDH InsurancePlan | https://build.fhir.org/ig/HL7/fhir-us-ndh/en/StructureDefinition-ndh-InsurancePlan.html |
| NDH Endpoint | https://build.fhir.org/ig/HL7/fhir-us-ndh/en/StructureDefinition-ndh-Endpoint.html |

