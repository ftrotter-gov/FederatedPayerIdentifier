# Reusing Plan-Net Data to Populate the National Directory

## Purpose

This document proposes a set of narrow, concrete changes that would let the
National Directory of Healthcare Providers & Services (NDH) populate its payer,
plan, and endpoint layer from Da Vinci PDex Plan-Net data that payers are
already required to publish.

The goal is burden reduction. Payers publish Plan-Net today under CMS-9115-F.
If NDH can consume that publication directly, the marginal cost to a payer of
appearing in the national directory approaches zero, and CMS gains directory
coverage without standing up a new data-collection program.

This is a proposal for discussion with CMS and the NDH work group. It is not a
description of implemented behavior.

## Version scope

Every cardinality, code, and mapping rule cited here was read from:

| Artifact | Version | Basis |
|---|---|---|
| Da Vinci PDex Plan-Net | **STU 1.1.0** | The version referenced by federal utilization; see [AllAtOnce.md](AllAtOnce.md) |
| NDH | **2.0.0-current** (CI build) | The only build carrying the Plan-Net mappings |
| US Core (via Plan-Net) | 3.1.1 | Plan-Net STU 1.1.0 derives Organization from US Core 3.1.1 |
| US Core (via NDH) | 6.1.0 | NDH 2.0.0 derives Organization from US Core 6.1.0 |

The US Core skew between the two is a real risk and is tracked as **P7** below.

---

## Finding 1 — NDH already ships executable Plan-Net to NDH maps

The NDH IG contains a [Plan-Net Mappings](https://build.fhir.org/ig/HL7/fhir-us-ndh/en/plannet-maps.html)
page with nine StructureMaps written in FHIR Mapping Language, plus supporting
ConceptMaps:

`PlanNetToNdhOrganizationSM`, `PlanNetToNdhInsurancePlanSM`,
`PlanNetToNdhEndpointSM`, `PlanNetToNdhNetworkSM`, `PlanNetToNdhLocationSM`,
`PlanNetToNdhHealthcareServiceSM`, `PlanNetToNdhOrganizationAffiliationSM`,
`PlanNetToNdhPractitionerSM`, `PlanNetToNdhPractitionerRoleSM`

The IG states the rationale plainly: *"Plan-Net does not derive from NDH, but
rather creates similar Profiles, extensions, CodeSystems, and ValueSets."* The
two guides are semantically close and syntactically incompatible, so the bridge
was written.

**The self-population mechanism is not a proposal. It is already balloted
content that is currently under-exploited.**

## Finding 2 — NDH's mandatory element set is a subset of Plan-Net's

For the three resources that carry payer, plan, and endpoint identity, every
element NDH makes mandatory is already mandatory (or stricter) in Plan-Net.

### Organization

| Element | Plan-Net STU 1.1.0 | NDH 2.0.0 | Effect |
|---|---|---|---|
| `active` | 1..1, pattern `true` | 1..1 MS, pattern `true` | satisfied |
| `type` | 1..* MS | 1..* MS | satisfied |
| `name` | 1..1 MS | 1..1 MS | satisfied |
| `address` | **1..\* MS** | **0..\* MS** | Plan-Net stricter |
| `meta.lastUpdated` | 1..1 | 1..1 | satisfied |
| `partOf` | 0..1 MS | 0..1 MS | satisfied |
| `telecom` | 0..* MS | 0..* MS | satisfied |
| `endpoint` | 0..* MS | 0..* MS | satisfied |
| `identifier` | 0..*; slices NPI 0..1, CLIA 0..1 | 0..* MS; slices NPI, CLIA, NAIC, TID | Plan-Net has fewer slices; open slice carries the rest |
| `alias` | 0..*, not MS | 0..* **MS** | NDH wants it more (not mandatory) |

### InsurancePlan

| Element | Plan-Net STU 1.1.0 | NDH 2.0.0 | Effect |
|---|---|---|---|
| `status` | 1..1 MS, fixed `active` | 1..1 MS, fixed `active` | satisfied |
| `type` | 1..1 MS | 1..1 MS | satisfied |
| `name` | 0..1 MS | 0..1 MS | satisfied |
| `alias` | 0..* MS | 0..*, not MS | satisfied |
| `ownedBy` | **1..1 MS** | **0..1, not MS** | Plan-Net stricter |
| `administeredBy` | **1..1 MS** | **0..1, not MS** | Plan-Net stricter |
| `coverageArea` | 0..* MS | 0..* MS | satisfied |
| `network` | 0..* MS | 0..* MS | satisfied |
| `endpoint` | 0..* MS | 0..*, not MS | satisfied |

### Endpoint

| Element | Plan-Net STU 1.1.0 | NDH 2.0.0 | Effect |
|---|---|---|---|
| `status` | 1..1 MS, fixed `active` | 1..1 MS, fixed `active` | satisfied |
| `connectionType` | 1..1 MS, `EndpointConnectionTypeVS` (extensible) | 1..1 MS, `EndpointConnectionTypeVS` (extensible) | ConceptMap handles Plan-Net-specific codes |
| `payloadType` | 1..1 MS, `EndpointPayloadTypeVS` (extensible) | 1..1, not MS | satisfied |
| `address` | 1..1 MS, url | 1..1, not MS | satisfied |
| `name` | 0..1 MS | 0..1 MS | satisfied |
| `managingOrganization` | 0..1 MS | 0..1 MS | satisfied |
| `payloadMimeType` | 0..* MS, **required** to Mime Types | 0..* MS, **required** to `EndpointFhirMimeTypeVS` | **NDH binding is narrower — see P8** |

### Conclusion

**A payer conformant to Plan-Net STU 1.1.0 already possesses every element NDH
makes mandatory for Organization, InsurancePlan, and Endpoint.** Not most of
them — all of them. Where the two guides differ on required elements, Plan-Net
is the stricter guide in every case.

This is the core burden argument: NDH's payer layer can be populated from
existing regulated publication with **no new payer data collection**.

## Finding 3 — The Endpoint map discards endpoint use-case data

`PlanNetToNdhEndpointSM` contains this rule, verbatim from the published FML:

```
src.extension as vDroppedEndpointUsecase
  where (url = 'http://hl7.org/fhir/us/davinci-pdex-plan-net/StructureDefinition/endpoint-usecase')
  "dropPlanNetEndpointUsecases";
```

The map faithfully carries `address`, `status`, `connectionType`, `payloadType`,
`payloadMimeType`, `name`, `managingOrganization`, `contact`, `identifier`,
`header`, `period`, and `meta.lastUpdated`. It then discards the only field that
records what the endpoint is for.

The practical result: a national directory populated by today's map contains
endpoints whose `connectionType` is `hl7-fhir-rest` and nothing more. There is
no way to distinguish a PAS submission endpoint from a CARIN Blue Button
endpoint from a provider directory endpoint.

This is precisely the failure that the payer well-known index exists to prevent,
and it is the single highest-leverage defect in the current pipeline.

Two smaller drops exist in `PlanNetToNdhOrganizationSM` (`org-description`,
`contactpoint-availabletime`, `via-intermediary`) and are lower priority.

## Finding 4 — NDH already defines the endpoint metadata model we need

`ndh-Endpoint` carries an `implementation-guide` extension that is a close
structural match for the well-known index's `plan_endpoints` keys:

| Sub-element | Card. | Type | Binding |
|---|---|---|---|
| `ig-uri` | 0..1 | **canonical** | — |
| `ig-name` | 0..1 | string | — |
| `ig-version` | 0..1 | string | — |
| `ig-usecase` | 0..* | CodeableConcept | `NdhImplementationGuideVS` (extensible, 53 codes) |
| `ig-actor` | 0..* | string | — |
| `ig-option` | 0..* | string | — |

The extension requires at least one of `ig-uri` or `ig-name`.

A well-known key such as `davinci_pas_submission_endpoint#1.2` decomposes
directly into `ig-uri` + `ig-version` + `ig-usecase`. The versioning problem
that Plan-Net cannot express — Plan-Net Endpoint has no version element, and
`endpoint-usecase.standard` is a plain `uri` rather than a `canonical` — is
already solved in NDH.

**This repository should stop treating a Plan-Net fork as the path to endpoint
typing. NDH has the model. The work is to route Plan-Net data into it.**

`NdhImplementationGuideVS` already covers `cdex`, `pasOperation`,
`payerAttachment`, `payerToPayer`, `patientAccess`, `providerApi`,
`coverage-requirements-discovery-crd`, `documentation-templates-rules-dtr`, and
`prior-authorization`. It does **not** cover PDex, Plan-Net itself, CARIN Blue
Button, PDex Formulary, or CARIN RTPBC.

## Finding 5 — Identifiers and unknown extensions already pass through

`PlanNetToNdhOrganizationSM` copies identifiers verbatim:

```
src.identifier as vIdentifier -> tgt.identifier = vIdentifier;
```

and copies every extension except `org-description` verbatim:

```
src.extension as vExtension
  where (url != 'http://hl7.org/fhir/us/davinci-pdex-plan-net/StructureDefinition/org-description')
  -> tgt.extension = vExtension;
```

**Consequence: a Federated Payer Identifier placed in a Plan-Net
`Organization.identifier` today flows into NDH with no map change at all.** The
same is true of an FPI-provenance extension. This is a far cheaper path to
linking the FPI into the national directory than any profile fork, and it can be
piloted before any IG change is balloted.

What it does not provide is validation or discoverability — the FPI lands in the
open identifier slice with no slice definition, no terminology registration, and
no invariant. That is the substance of **P6**.

## Finding 6 — There is no ingestion path and no harvest provenance

Two structural gaps:

1. The [NDH Server CapabilityStatement](https://build.fhir.org/ig/HL7/fhir-us-ndh/en/CapabilityStatement-ndh-server.html)
   describes a read and search server. There is an `ndhschexport` operation for
   data flowing *out*. The [Attestation and Verification Guidance](https://build.fhir.org/ig/HL7/fhir-us-ndh/en/avv-guide.html)
   describes practitioners, organizations, payers, and intermediaries submitting
   data *in*. **Nothing describes NDH retrieving data from an entity's own
   already-published conformant endpoint** — the exact motion this proposal
   depends on.

2. `VerificationProcessVS` contains nine codes — `edit-check`, `valueset`,
   `primary`, `multi`, `standalone`, `in-context`, `manual`, `attester`,
   `extsource`. **None means "automatically retrieved from the entity's own
   published conformant API."** `extsource` ("External source") is the nearest
   and is actively misleading: a payer's own Plan-Net server is a self-published
   primary source, not an external one.

Without a provenance code, harvested content cannot be distinguished from
attested content, and the correction loop has no anchor.

---

## Proposed changes

Ordered by leverage relative to effort. Owner is the group that would carry the
change.

### P1 — Translate `endpoint-usecase` instead of dropping it

**Owner: NDH.** Replace the `dropPlanNetEndpointUsecases` rule in
`PlanNetToNdhEndpointSM` with a translation into `implementation-guide`, mapping
`endpoint-usecase.standard` (uri) to `ig-uri` (canonical) and
`endpoint-usecase.type` through a new ConceptMap to `ig-usecase`.

Illustrative shape — this needs FML validation before it is proposed formally:

```
src.extension as vUsecase where (url = 'http://hl7.org/fhir/us/davinci-pdex-plan-net/StructureDefinition/endpoint-usecase')
  -> tgt.extension as vIg then {
    vUsecase -> vIg.url = 'http://hl7.org/fhir/us/ndh/StructureDefinition/base-ext-implementation-guide' "setIgUrl";
    vUsecase.extension as vStd where (url = 'standard') -> vIg.extension as vIgUri then {
      vStd.value as v -> vIgUri.url = 'ig-uri', vIgUri.value = v "setIgUri";
    } "mapStandard";
    vUsecase.extension as vType where (url = 'type') -> vIg.extension as vIgUse then {
      vType.value as v -> vIgUse.url = 'ig-usecase',
        vIgUse.value = translate(v, 'http://hl7.org/fhir/us/ndh/ConceptMap/plannet-to-ndh-endpoint-usecase', 'CodeableConcept') "setIgUsecase";
    } "mapType";
  } "mapEndpointUsecase";
```

Note that the source vocabulary is coarse: Plan-Net's `EndpointUsecaseVS` holds
nine `v3-ActReason` codes (`TREAT`, `HPAYMT`, `COC`, `COVERAGE`, `HOPERAT`,
`PUBHLTH`, `HRESCH`, `ETREAT`, `PATRQT`). These cannot distinguish CRD from PAS.
The real fidelity comes from `standard` to `ig-uri`, which is why that half of
the mapping matters most.

**Effort: days. Value: converts the existing pipeline from lossy to useful.**

### P2 — Add the missing payer IG codes to `NdhImplementationGuideVS`

**Owner: NDH.** Add codes for PDex, PDex Plan-Net, CARIN Blue Button, PDex
Formulary, and CARIN RTPBC. Roughly five to eight codes against an existing
53-code value set.

**Effort: a terminology pull request. Not an IG fork.**

### P3 — Make `implementation-guide` an obligation for payer-published endpoints

**Owner: NDH.** The extension is currently `0..*` and **not Must Support**. A
payer can be fully NDH-conformant while saying nothing about what any of its
endpoints does.

Express this as a FHIR **Obligation** (`SHALL:populate`) bound to a payer actor
rather than as a cardinality change, so the requirement lands on payers without
re-profiling for every other NDH participant. At minimum require `ig-uri` and
`ig-version`.

This is also the general answer to expressing "fully populated" conformance
without forking an IG or shipping a constrained `package.tgz`.

### P4 — Define a harvest path and a harvest provenance code

**Owner: NDH.** Three parts:

1. Define a harvesting actor and its conformance expectations: NDH retrieving
   from a payer's published Plan-Net base URL.
2. Add a `VerificationProcessVS` code for automated retrieval from an entity's
   own published conformant API. Do not overload `extsource`.
3. Record the retrieval URL and timestamp in an `ndh-Verification`
   (VerificationResult) instance attached to each harvested resource.

This is what makes the policy posture defensible: *"we took what you already
published, here is exactly what we took and when, correct it if it is wrong."*
Attestation by exception rather than attestation by re-keying.

### P5 — Promote `InsurancePlan` from SHOULD to SHALL

**Owner: NDH.** The NDH Server CapabilityStatement lists `InsurancePlan` as
SHOULD support, alongside `Group`, while `Organization`, `Endpoint`,
`Practitioner`, and others are SHALL. If payer and plan identity is in scope for
the national directory, the resource carrying it should not be optional to
support.

### P6 — Give the FPI a defined home in NDH

**Owner: NDH, with this repository.** Per Finding 5, an FPI in
`Organization.identifier` already reaches NDH unchanged. To make it valid rather
than merely tolerated:

1. Add an FPI identifier slice to `ndh-Organization` alongside NPI, CLIA, NAIC,
   and TID.
2. Register the FPI identifier system canonically.
3. Add an invariant that an Organization carries at most one FPI.

Note that both Plan-Net and NDH fix NAIC to `urn:oid:2.16.840.1.113883.6.300`
with a five-digit constraint. This repository currently uses
`https://directory.cms.gov/payer_identification_system/naic_id`. Conceding to
the OID form for NAIC costs this project nothing and removes an avoidable
argument. See [WellKnownFileFormat.md](WellKnownFileFormat.md).

### P7 — Pin the StructureMaps to a Plan-Net version

**Owner: NDH.** The maps declare unversioned canonicals:

```
uses "http://hl7.org/fhir/us/davinci-pdex-plan-net/StructureDefinition/plannet-Endpoint" alias EndpointPN as source
```

Given that regulation points at STU 1.1.0, the maps should pin `|1.1.0`
explicitly. Unpinned canonicals resolve against whatever Plan-Net version is in
the package cache, and Plan-Net 2.0.0-ballot differs materially from 1.1.0 — it
adds an `MA-PLAN-ID` identifier slice to InsurancePlan and a NAIC slice to
Organization, neither of which exists in 1.1.0.

Related: Plan-Net STU 1.1.0 derives Organization from **US Core 3.1.1**, while
NDH 2.0.0 derives from **US Core 6.1.0**. This skew spans several US Core major
versions and will affect map execution and validation. It needs its own
analysis.

### P8 — Resolve the `payloadMimeType` binding conflict

**Owner: NDH.** Plan-Net binds `Endpoint.payloadMimeType` required to the
general Mime Types value set. NDH binds it required to `EndpointFhirMimeTypeVS`.
A Plan-Net endpoint carrying a non-FHIR mime type — which is legitimate, since
Plan-Net STU 1.1.0 includes the `rest-non-fhir` connection type — will fail NDH
validation on ingest.

Either widen the NDH value set, or have the map filter non-conformant values
with a recorded warning rather than producing an invalid resource.

### P9 — Reduce the well-known index to a bootstrap artifact

**Owner: this repository.** If P1 through P8 land, most of what the well-known
index carries today becomes derived output rather than curated input. See the
next section.

---

## What remains in the well-known index

Plan-Net states that *"this implementation guide assumes that the directory
endpoint is known to the client"* and places discovery out of scope. NDH is the
natural answer to discovery, but cannot harvest a server whose address it does
not have.

That circularity is what the well-known index resolves, and it is why the file
does not shrink to nothing. The irreducible remainder:

| Content | Why it cannot move into Plan-Net or NDH |
|---|---|
| FPI, `fpi_source_system`, `fpi_source_value` | No defined home until P6 lands; the provenance fields have no counterpart in either guide |
| **The payer's Plan-Net base URL** | The bootstrap. Neither guide provides discovery. |
| Non-FHIR endpoints: TiC MRF index (per issuer), payer homepage, documentation URL, FHIR signup URL, all-at-once NDJSON | Outside Plan-Net's scope; the per-issuer TiC discriminator has no home in either guide |
| Negative assertions (`"key": null`) | Not expressible. `Endpoint.status` is fixed to `active` and `address` is 1..1 in both guides, so "we know about this protocol and do not offer it" cannot be stated. |
| Payer / plan-group / plan string-search scoping | `alias` exists at Organization and InsurancePlan level, but the three-level scoping collapses |
| `copied_from_url`, `is_seeded` | Repository workflow state, not directory content. Correctly out of scope for any standard. |

The roughly 800 seeded Medicare Advantage records in
[payer_index_files](payer_index_files) then stop being a data-entry liability
and become a crawl list.

---

## Open questions and risks

1. **Have the StructureMaps ever been executed against real payer Plan-Net
   data?** A map that has only been validated syntactically is a hypothesis. This
   should be tested before it is presented as a foundation.
2. **US Core 3.1.1 to 6.1.0 skew** (P7) is the largest unquantified technical
   risk in this proposal.
3. **Harvest cadence and the correction loop.** Who runs the harvest, how often,
   and how does a payer dispute or correct a harvested record? P4 defines the
   provenance but not the operational process.
4. **Legal authority to harvest.** Plan-Net publication is a public,
   unauthenticated, query-only API by design. Whether that constitutes consent to
   national-directory republication is a policy question, not a technical one.
5. **`ig-usecase` fidelity.** Plan-Net's nine `v3-ActReason` codes cannot
   distinguish most payer IGs. Endpoints that omit `endpoint-usecase.standard`
   will produce low-value NDH records even after P1.

---

## Summary for CMS

Payers already publish Plan-Net under CMS-9115-F. NDH already contains
executable Plan-Net to NDH StructureMaps. NDH's mandatory elements for payers,
plans, and endpoints are a strict subset of Plan-Net's.

The national directory's payer layer can therefore be populated with no new
payer data collection, provided that NDH stops discarding endpoint use-case
data, adds a handful of payer IG codes, defines a harvest path with honest
provenance, and gives the federated payer identifier a defined home. A minimal
payer-controlled well-known index supplies the discovery bootstrap that neither
guide provides.

Everything else required is already balloted.
