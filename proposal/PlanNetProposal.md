# Proposed Changes to Da Vinci PDex Plan-Net to Support Insurance-Card-to-Endpoint Routing

## Purpose

This document proposes a set of concrete, narrow changes to the
**Da Vinci PDex Plan-Net Implementation Guide** (`hl7.fhir.us.davinci-pdex-plan-net`)
that would allow a patient's insurance card information to be used to discover
the correct interoperability endpoints for that payer and plan.

This is the same problem currently solved by the payer well-known index in the Federal Provider Identifier repo.

The argument here is that Plan-Net — which payers are already
required to publish under CMS-9115-F — can carry all of this information,
provided the right elements are promoted to **MustSupport** and the right
identifier requirements are added.

There may also need to be specific additional contraints on what might otherwise be
"implementation choices" within the PlanNet specification.

**MustSupport is the heart of this proposal.** In FHIR, marking an element
MustSupport means that any payer claiming conformance to Plan-Net must be
capable of populating that element, and any API consumer must be capable of
processing it. Without MustSupport, an element is optional in both directions
and cannot be relied upon for the critical interoperability use-cases.
(i.e. resolving Patient Insurance Cards to Payer FHIR Endpoints)

MustSupport also governs the **"send if known"** obligation. An element with
cardinality `0..*` and MustSupport is not required to be present — but if the
payer has the data, they **must** send it. A payer whose legal name is also
their only public name may omit `Organization.alias`. A payer who operates
under trade names or abbreviations must populate it. This "send if known"
pattern is how Plan-Net can impose real conformance obligations on optional
data without making every element unconditionally mandatory.

Because thousands of payers will be tested against Plan-Net conformance,
MustSupport — including its "send if known" obligation — is the mechanism that
gives requirements real impact from an interoperability perspective.

The National Directory of Healthcare Providers & Services (NDH) already
contains executable StructureMaps that translate Plan-Net resources into NDH
resources. That bridge is already balloted content. This proposal focuses on
what Plan-Net needs to publish correctly — NDH is mentioned only where it has a
capability gap that Plan-Net changes alone cannot fix.

This is a proposal for discussion with the Da Vinci Plan-Net work group and others in the FHIR community.
It is not a description of implemented behavior.

---

## The Routing Problem

A patient's insurance card typically carries a payer name (often a trade name),
a plan name or group identifier, and a member ID. From these, a downstream
system needs to find the correct legal payer entity, the correct plan, and the
correct interoperability endpoints for that plan (prior auth, patient access,
provider directory, formulary, etc.).

The payer well-known index in the Federal Provider Identifier repo is one proposal to solve this problem.
This is a second proposal to show how Plan-Net — already mandatory publication — can
carry the same information, making the well-known index a minimal bootstrap
artifact rather than the primary source of truth.

---

## Summary of Proposed Plan-Net Changes

| ID | Resource | Element | Change |
|---|---|---|---|
| P1 | `plannet-Organization` | `identifier` | Add `1..1 MS` FPI identifier slice |
| P2 | `plannet-Organization` | `identifier` (HIOS, NAIC, etc.) | Promote existing payer-ID slices to MustSupport |
| P3 | `plannet-Organization` | `telecom` (`system=url`) | Add `1..1 MS` contact-URL slice |
| P4 | `plannet-Organization` | `alias` | Promote to MustSupport ("send if known") |
| P5 | `plannet-InsurancePlan` | `contact.telecom` (`system=url`) | Add `1..1 MS` contact-URL slice |
| P6 | `plannet-Endpoint` | `extension:endpoint-usecase` | Promote to MustSupport |
| P7A | `plannet-Endpoint` | `endpoint-usecase.type` + `standard` | Define `PlanNetEndpointTypeCS`; rebind `type`; promote `standard` to `1..1 MS` *(Approach A — recommended)* |
| P7B | `plannet-Endpoint` | new extension | Define `endpoint-ig-conformance` with `ig-type` + `ig-version` *(Approach B — alternative)* |
| P8 | Plan-Net guidance | (documentation) | Document the multiple-version Endpoint pattern |

---

## Proposed Changes

### P1 — Add a MustSupport FPI identifier slice to `plannet-Organization`

Add an identifier slice with `system` fixed to the FPI canonical
(`https://directory.cms.gov/payer_identification_system/fpi`) and cardinality
`1..1 MS`. Without this, Plan-Net publication does not produce a persistently
addressable payer identity. This is the single most important change in this
proposal.

### P2 — Promote payer-specific identifier slices to MustSupport

The open slice on `Organization.identifier` already permits HIOS IDs, NAIC
codes, and other routing identifiers. Promoting the relevant slices to
MustSupport requires payers to publish the identifiers that appear on insurance
cards. HIOS ID and NAIC code are the strongest candidates. CMS contract numbers
identify contracts rather than legal entities and should not be defaulted to.

### P3 — Add a MustSupport contact-URL slice to `plannet-Organization`

Add a slice on `Organization.telecom` with `system` fixed to `url` and
cardinality `1..1 MS`. This provides a mandatory, testable primary contact
website — the `payerContactWebsite` field in the well-known index.

### P4 — Promote `Organization.alias` to MustSupport

`alias` is present in Plan-Net but not MustSupport. Promoting it applies the
"send if known" obligation: payers with trade names, abbreviations, or brand
names must publish them. Payers whose legal name is their only public name may
omit it. This enables string-search routing from an insurance card that carries
a name other than the payer's legal name.

### P5 — Add a MustSupport contact-URL slice to `plannet-InsurancePlan`

Add a slice on `InsurancePlan.contact.telecom` with `system` fixed to `url`
and cardinality `1..1 MS`. This provides a testable plan-level contact website,
equivalent to the `plan_homepage` entries in the well-known index.
`InsurancePlan.name` and `alias` are already MustSupport and require no change.

### P6 — Promote `endpoint-usecase` to MustSupport

`endpoint-usecase` is present in Plan-Net STU 1.1.0 but is not MustSupport,
so payers routinely omit it. Without it, endpoints carry only a
`connectionType` of `hl7-fhir-rest` with no indication of which IG they
implement. A URL alone cannot tell a consumer which IG is running. This
promotion is required for both Approach A and Approach B.

### P7 — Fix the endpoint type vocabulary and require a version (choose A or B)

The `endpoint-usecase.type` field is bound to `EndpointUsecaseVS`, which draws
from `v3-ActReason` — a HIPAA administrative purpose vocabulary whose codes
(`TREAT`, `HOPERAT`, etc.) answer *why* data is exchanged, not *which IG* an
endpoint implements. Both approaches below replace this with a purpose-built
CodeSystem.

**`PlanNetEndpointTypeCS` — one code per named IG, version lives separately:**

| Code | IG |
|---|---|
| `davinci-crd` | Da Vinci Coverage Requirements Discovery |
| `davinci-pas` | Da Vinci Prior Authorization Support |
| `davinci-cdex` | Da Vinci Clinical Data Exchange |
| `davinci-pdex-formulary` | Da Vinci PDex Formulary |
| `davinci-pdex-provider-directory` | Da Vinci PDex Plan-Net provider directory |
| `davinci-payer-to-payer` | Da Vinci Payer-to-Payer |
| `davinci-pdex-patient-access` | Da Vinci PDex Patient Access |
| `carin-bluebutton` | CARIN Blue Button patient access |
| `carin-rtpbc` | CARIN Real-Time Pharmacy Benefit Check |

A new IG version never adds a code — it adds a new `Endpoint` resource with a
new version value. A genuinely new IG adds one code.

**Approach A (recommended)** — Rebind `endpoint-usecase.type` to a value set
drawing from `PlanNetEndpointTypeCS`. Promote `standard` from `0..1` to
`1..1 MS`, carrying the IG version string (e.g. `"2.0.0"`). The JSON shape of
the extension is unchanged:

```json
{
  "url": "http://hl7.org/fhir/us/davinci-pdex-plan-net/StructureDefinition/endpoint-usecase",
  "extension": [
    { "url": "type", "valueCodeableConcept": { "coding": [{
        "system": "http://hl7.org/fhir/us/davinci-pdex-plan-net/CodeSystem/PlanNetEndpointTypeCS",
        "code": "davinci-crd" }] } },
    { "url": "standard", "valueUri": "2.0.0" }
  ]
}
```

**Approach B (alternative)** — Leave `endpoint-usecase` unchanged for its
original HIPAA administrative purpose. Define a new extension
`endpoint-ig-conformance` with `ig-type` (CodeableConcept from
`PlanNetEndpointTypeCS`, `1..1 MS`) and `ig-version` (string, `1..1 MS`).
Cleaner separation of concerns, but higher balloting cost and requires new NDH
StructureMap rules rather than a simple fix to the existing drop.

### P8 — Document the multiple-version Endpoint pattern

When a payer supports multiple versions of the same IG simultaneously, each
version is published as a separate `Endpoint` resource with its own type code
and version value. This is a documentation and testability change only.

---

## What Remains in the Well-Known Index

| Field | Why Plan-Net cannot express it |
|---|---|
| **The payer's Plan-Net base URL** | Plan-Net assumes the endpoint is already known to the client; discovery is out of scope |
| **Per-issuer TiC MRF URLs** | The per-issuer discriminator has no structural home in Plan-Net |
| **Negative assertions** (`"key": null`) | `Endpoint.status` is fixed `active` and `address` is `1..1`; "we do not offer this protocol" cannot be stated |
| **Repository workflow fields** (`is_seeded`, `copied_from_url`) | Correctly out of scope for any standard |

---

## Open Questions

1. **Which payer identifier slices should be promoted under P2?** HIOS ID and
   NAIC code are the strongest candidates. CMS contract numbers identify
   contracts rather than legal entities and should not be defaulted to.

2. **What is the version string format for P7A (`standard`) or P7B (`ig-version`)?**
   Bare semver (`"2.0.0"`), full versioned canonical URI, or something else?
   Needs agreement across Da Vinci work groups before an invariant can be written.

3. **How are non-FHIR URLs (payer homepage, documentation page) best expressed
   in Plan-Net?** If there is no clean fit, these fields remain in the
   well-known index.
