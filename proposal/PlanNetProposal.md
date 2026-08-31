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

Because thousands of payers will be tested against Plan-Net conformance, 
MustSupport is the mechanism that gives requirements impact from an interoperability perspective.

The National Directory of Healthcare Providers & Services (NDH) already
contains executable StructureMaps that translate Plan-Net resources into NDH
resources. That bridge is already balloted content. This proposal focuses on
what Plan-Net needs to publish correctly — NDH is mentioned only where it has a
capability gap that Plan-Net changes alone cannot fix.

This is a proposal for discussion with the Da Vinci Plan-Net work group and others in the FHIR community. 
It is not a description of implemented behavior.

---

## Version Scope

| Artifact | Version |
|---|---|
| Da Vinci PDex Plan-Net | **STU 1.1.0** (federally mandated under CMS-9115-F) |
| NDH | **2.0.0-current** (CI build; carries the Plan-Net StructureMaps) |

---

## The Routing Problem

A patient's insurance card typically carries a payer name (often a trade name),
a plan name or group identifier, and a member ID. From these, a downstream
system needs to find the correct legal payer entity, the correct plan, and the
correct interoperability endpoints for that plan (prior auth, patient access,
provider directory, formulary, etc.).

The payer well-known index in this repository is one proposal to solve this problem.
This is a second proposal to show how Plan-Net — already mandatory publication — can
carry the same information, making the well-known index a minimal bootstrap
artifact rather than the primary source of truth.

---

## Layer 1 — Payer Identity (`plannet-Organization`)

### What is needed

A conformant Plan-Net `Organization` resource for a payer must carry enough
information to:

1. Uniquely and persistently identify the legal payer entity (the Federated
   Payer Identifier).
2. Crosswalk to other payer identifier systems (HIOS, NAIC, CMS contract, etc.)
   used on insurance cards and in claims routing.
3. Surface the payer's primary contact website.
4. Support string-search discovery by consumers who know only a trade name or
   abbreviation.

### Current Plan-Net STU 1.1.0 gaps

| Element | Current status | Gap |
|---|---|---|
| `Organization.identifier` (FPI slice) | No FPI slice defined | Payers have no standard place to publish their Federated Payer Identifier |
| `Organization.identifier` (HIOS, NAIC, etc.) | Open slice; payer-specific slices not MustSupport | Cannot be relied upon for routing |
| `Organization.telecom` (`system=url`) | `0..* MS` but no slice requiring a URL | No guaranteed contact website |
| `Organization.alias` | `0..* not MS` | Trade names are optional and ignorable; string-search routing is unreliable |

### Proposed Plan-Net changes

**P1 — Add a MustSupport FPI identifier slice to `plannet-Organization`.**

Add an identifier slice with `system` fixed to the FPI canonical
(`https://directory.cms.gov/payer_identification_system/fpi`) and cardinality
`1..1 MS`. This makes the Federated Payer Identifier a mandatory, testable
element of every Plan-Net payer Organization.

This is the single most important change in this proposal. Without it,
Plan-Net publication does not produce a persistently addressable payer identity.

**P2 — Promote payer-specific identifier slices to MustSupport.**

The open slice on `Organization.identifier` already allows HIOS IDs, NAIC
codes, and other routing identifiers. Promote the relevant slices to MustSupport
so that payers are required to publish the identifiers that appear on insurance
cards and in claims systems. HIOS ID and NAIC code are the strongest candidates.
CMS contract numbers identify contracts rather than legal entities and should
not be defaulted to.

**P3 — Add a MustSupport contact-URL telecom slice to `plannet-Organization`.**

Add a slice on `Organization.telecom` with `system` fixed to `url` and
cardinality `1..1 MS`. This gives every payer Organization a mandatory,
testable primary contact website — the `payerContactWebsite` field in the
current well-known index.

**P4 — Promote `Organization.alias` to MustSupport.**

`alias` is currently present in Plan-Net but not MustSupport. Promoting it to
MS means payers must publish their trade names, abbreviations, and brand names.
This is what enables string-search routing from an insurance card that carries
a name other than the payer's legal name.

---

## Layer 2 — Plan Identity (`plannet-InsurancePlan`)

### What is needed

A conformant Plan-Net `InsurancePlan` resource must carry enough information to:

1. Identify the plan by name.
2. Support string-search discovery by consumers who know only a marketing name
   or abbreviation.
3. Surface the plan's own contact website where one exists.
4. Be reliably linked back to the payer Organization.

### Current Plan-Net STU 1.1.0 status and gaps

| Element | Current status | Gap |
|---|---|---|
| `InsurancePlan.name` | `0..1 MS` | Sufficient; no change needed |
| `InsurancePlan.alias` | `0..* MS` | Already MustSupport; no change needed |
| `InsurancePlan.ownedBy` | `1..1 MS` | Links to payer Organization; sufficient |
| `InsurancePlan.contact` (website, `system=url`) | `0..* not MS` | No guaranteed plan-level contact website |

### Proposed Plan-Net changes

**P5 — Add a MustSupport contact-URL slice to `plannet-InsurancePlan`.**

Add a slice on `InsurancePlan.contact.telecom` with `system` fixed to `url`
and cardinality `1..1 MS`. This provides a testable plan-level contact website,
equivalent to the `plan_homepage` entries in the current well-known index.

---

## Layer 3 — Endpoints (`plannet-Endpoint` and `endpoint-usecase`)

### What is needed

Endpoints are the payload of routing. A downstream system that has found the
right payer and plan needs to know:

- What protocol the endpoint speaks (FHIR REST, bulk, non-FHIR).
- Which Implementation Guide the endpoint implements (e.g. Da Vinci CRD,
  CARIN Blue Button, Da Vinci PDex Formulary).
- Which **version** of that IG the endpoint implements.
- The URL.

The current well-known index encodes this as structured keys like
`davinci_crd_hook#2.0` pointing to a URL. Plan-Net already has structural
machinery to express this — it just is not required to use it, and its current
type vocabulary is the wrong vocabulary for the job.

### The current `endpoint-usecase` structure and its type binding problem

The `endpoint-usecase` extension has two sub-elements:

| Sub-element | Type | Card. | Current binding |
|---|---|---|---|
| `type` | CodeableConcept | 1..1 MS | `EndpointUsecaseVS` (extensible) |
| `standard` | uri | 0..1 MS | none |

The `type` binding is the core problem. `EndpointUsecaseVS` draws from the
HL7 `v3-ActReason` code system — a HIPAA administrative purpose vocabulary.
Its nine codes answer **why** data is being exchanged (`TREAT`, `HPAYMT`,
`HOPERAT`, etc.), not **which IG** an endpoint implements. Every payer FHIR
endpoint would legitimately receive `TREAT` or `HOPERAT`. A URL alone cannot
tell a consumer which IG is implemented — experience shows that
`https://example.org/fhir/v1/` could be anything. The `v3-ActReason` codes
make this no better. They are the wrong vocabulary for routing.

### Expressing multiple versions of the same IG

The well-known index uses separate keys (`davinci_crd_hook#1.1` and
`davinci_crd_hook#2.0`) to express that a payer supports two versions of the
same IG simultaneously. In Plan-Net, this is expressed by publishing **two
separate `Endpoint` resources**, each with its own type and version. The
pattern must be **explicitly documented** in Plan-Net guidance and must be
testable, which requires the endpoint type mechanism to be MustSupport.

### Two approaches to fixing endpoint typing

Both approaches require defining the same new CodeSystem — `PlanNetEndpointTypeCS`
— with one code per named IG. The version lives separately, in `standard` or
an equivalent field. The vocabulary therefore stays flat and finite: a new IG
version adds a new `Endpoint` resource with a new version string, not a new
code. A genuinely new IG adds one code. That is the entire maintenance model.

Example codes for `PlanNetEndpointTypeCS`:

| Code | IG |
|---|---|
| `davinci-crd` | Da Vinci Coverage Requirements Discovery |
| `davinci-pas` | Da Vinci Prior Authorization Support |
| `davinci-cdex` | Da Vinci Clinical Data Exchange |
| `davinci-pdex-formulary` | Da Vinci PDex Formulary |
| `davinci-pdex-provider-directory` | Da Vinci PDex Plan-Net provider directory |
| `davinci-provider-payer-access` | Da Vinci Provider-Payer Access |
| `davinci-payer-to-payer` | Da Vinci Payer-to-Payer |
| `davinci-pdex-patient-access` | Da Vinci PDex Patient Access |
| `carin-bluebutton` | CARIN Blue Button patient access |
| `carin-rtpbc` | CARIN Real-Time Pharmacy Benefit Check |

#### Approach A — Replace the type CodeSystem, keep the existing extension

Rebind `endpoint-usecase.type` to a new value set drawing from
`PlanNetEndpointTypeCS`. Promote `standard` to `1..1 MS` carrying the IG
version string (e.g. `"2.0.0"`). The JSON shape of the extension is
**unchanged**. The NDH StructureMap needs only to stop dropping the extension
— no structural rewrite required.

**JSON — Da Vinci CRD 2.0:**
```json
{
  "extension": [{
    "url": "http://hl7.org/fhir/us/davinci-pdex-plan-net/StructureDefinition/endpoint-usecase",
    "extension": [
      { "url": "type", "valueCodeableConcept": { "coding": [{
          "system": "http://hl7.org/fhir/us/davinci-pdex-plan-net/CodeSystem/PlanNetEndpointTypeCS",
          "code": "davinci-crd" }] } },
      { "url": "standard", "valueUri": "2.0.0" }
    ]
  }],
  "status": "active",
  "connectionType": { "system": "...", "code": "hl7-fhir-rest" },
  "address": "https://example.org/fhir/crd"
}
```

**JSON — same payer, CRD 1.1 also supported (separate Endpoint resource):**
```json
{
  "extension": [{
    "url": "http://hl7.org/fhir/us/davinci-pdex-plan-net/StructureDefinition/endpoint-usecase",
    "extension": [
      { "url": "type", "valueCodeableConcept": { "coding": [{
          "system": "http://hl7.org/fhir/us/davinci-pdex-plan-net/CodeSystem/PlanNetEndpointTypeCS",
          "code": "davinci-crd" }] } },
      { "url": "standard", "valueUri": "1.1.0" }
    ]
  }],
  "status": "active",
  "connectionType": { "system": "...", "code": "hl7-fhir-rest" },
  "address": "https://example.org/fhir/crd/v1"
}
```

#### Approach B — Define a new purpose-built extension

Leave `endpoint-usecase` unchanged for its original HIPAA administrative
purpose. Define a new Plan-Net extension — `endpoint-ig-conformance` — with
two MustSupport fields: `ig-type` (CodeableConcept, drawing from
`PlanNetEndpointTypeCS`) and `ig-version` (string). Clean separation of
concerns, at the cost of balloting a new extension and requiring new NDH
StructureMap rules rather than a simple fix to the existing drop.

**JSON — Da Vinci CRD 2.0 under Approach B:**
```json
{
  "extension": [{
    "url": "http://hl7.org/fhir/us/davinci-pdex-plan-net/StructureDefinition/endpoint-ig-conformance",
    "extension": [
      { "url": "ig-type", "valueCodeableConcept": { "coding": [{
          "system": "http://hl7.org/fhir/us/davinci-pdex-plan-net/CodeSystem/PlanNetEndpointTypeCS",
          "code": "davinci-crd" }] } },
      { "url": "ig-version", "valueString": "2.0.0" }
    ]
  }],
  "status": "active",
  "connectionType": { "system": "...", "code": "hl7-fhir-rest" },
  "address": "https://example.org/fhir/crd"
}
```

### Proposed Plan-Net changes

**P6 — Promote `endpoint-usecase` to MustSupport.** *(required for both approaches)*

Without this, the entire endpoint routing problem remains unsolved in Plan-Net
regardless of any other changes. The NDH StructureMap currently silently drops
this extension; MustSupport is what makes dropping it a conformance failure.

**P7A — Define `PlanNetEndpointTypeCS`, rebind `endpoint-usecase.type`, and
promote `standard` to `1..1 MS`.** *(Approach A — recommended)*

Minimum change. Existing extension shape preserved. NDH StructureMap fix is
a one-line change. The work group adds codes as new IGs are published.

**P7B — Define `endpoint-ig-conformance` as a new purpose-built extension.**
*(Approach B — alternative)*

Cleaner separation of concerns. Higher balloting cost. Requires new NDH
StructureMap rules. Recommended only if the work group determines that
repurposing `endpoint-usecase` is not acceptable.

**P8 — Document the multiple-version Endpoint pattern.** *(both approaches)*

Add a guidance section to Plan-Net stating that when a payer supports multiple
versions of the same IG, each version is published as a separate `Endpoint`
resource with a distinct version value. Documentation and testability change
only.

---

## What Remains in the Well-Known Index

Even with all of the above Plan-Net changes, certain fields in the well-known
index cannot be expressed in Plan-Net and must remain in a thin bootstrap file:

| Field | Why Plan-Net cannot express it |
|---|---|
| **The payer's Plan-Net base URL** | Plan-Net explicitly assumes the endpoint is already known to the client; discovery is out of scope for the IG |
| **Per-issuer TiC MRF URLs** (`tic_table_of_contents#issuer-XXXXX`) | The per-issuer discriminator has no structural home in Plan-Net |
| **Negative assertions** (`"key": null`) | `Endpoint.status` is fixed to `active` and `address` is `1..1`; "we know about this protocol and do not support it" cannot be stated |
| **Repository workflow fields** (`is_seeded`, `copied_from_url`) | Correctly out of scope for any standard |

The roughly 800 seeded Medicare Advantage records in this repository then stop
being a data-entry liability and become a crawl list derived from Plan-Net
publication.

---

## Summary of Proposed Plan-Net Changes

| ID | Resource | Element | Change |
|---|---|---|---|
| P1 | `plannet-Organization` | `identifier` | Add `1..1 MS` FPI slice |
| P2 | `plannet-Organization` | `identifier` (HIOS, NAIC, etc.) | Promote existing slices to MustSupport |
| P3 | `plannet-Organization` | `telecom` (`system=url`) | Add `1..1 MS` contact-URL slice |
| P4 | `plannet-Organization` | `alias` | Promote to MustSupport |
| P5 | `plannet-InsurancePlan` | `contact.telecom` (`system=url`) | Add `1..1 MS` contact-URL slice |
| P6 | `plannet-Endpoint` | `extension:endpoint-usecase` | Promote to MustSupport (required for both approaches) |
| P7A | `plannet-Endpoint` | `endpoint-usecase.type` + `standard` | Define `PlanNetEndpointTypeCS`; rebind `type`; promote `standard` to `1..1 MS` *(Approach A — recommended)* |
| P7B | `plannet-Endpoint` | new extension | Define `endpoint-ig-conformance` with `ig-type` + `ig-version` fields *(Approach B — alternative)* |
| P8 | Plan-Net guidance | (documentation) | Document multiple-version Endpoint pattern (both approaches) |

---

## Open Questions

1. **Which payer identifier slices should be promoted under P2?** The answer
   depends on which identifiers appear on insurance cards in practice. HIOS ID
   and NAIC code are the strongest candidates. CMS contract numbers identify
   contracts rather than legal entities and should not be defaulted to.

2. **Have the NDH StructureMaps ever been executed against real payer Plan-Net
   data?** A map that has only been validated syntactically is a hypothesis.
   Testing against real payer data is a prerequisite before presenting this
   pipeline as a production foundation.

3. **What is the canonical version string format for `endpoint-usecase.standard` (P7A) or `ig-version` (P7B)?**
   Should this be a bare semver string (`"2.0.0"`), a full versioned canonical
   URI, or something else? This needs agreement across Da Vinci work groups
   before an invariant can be written.

4. **How are non-FHIR URLs (payer homepage, documentation page) best expressed
   in Plan-Net?** The `rest-non-fhir` connection type exists, but using it for
   a plain informational website needs clarification. If there is no clean fit,
   these fields remain in the well-known index.
