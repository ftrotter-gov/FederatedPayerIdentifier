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
- Which Implementation Guide and version the endpoint implements (e.g.
  Da Vinci CRD 1.1, Da Vinci CRD 2.0, CARIN Blue Button 2.0).
- The URL.

The current well-known index encodes this as structured keys like
`davinci_crd_hook#2.0` pointing to a URL. Plan-Net already has the structural
machinery to express this — it just is not required to use it.

### The MustSupport gap: `endpoint-usecase`

Plan-Net's `endpoint-usecase` extension carries exactly the information needed:
a `type` (what the endpoint is for) and a `standard` (a URI identifying the IG
and version). This extension is present in Plan-Net STU 1.1.0 but is **not
MustSupport**.

The consequence is that the existing NDH StructureMap
(`PlanNetToNdhEndpointSM`) silently **discards** it:

```
src.extension as vDroppedEndpointUsecase
  where (url = 'http://hl7.org/fhir/us/davinci-pdex-plan-net/StructureDefinition/endpoint-usecase')
  "dropPlanNetEndpointUsecases";
```

Without MustSupport on `endpoint-usecase`, a national directory populated from
Plan-Net contains endpoints whose `connectionType` is `hl7-fhir-rest` and
nothing more. There is no way to distinguish a prior authorization endpoint
from a patient access endpoint from a provider directory endpoint. This is
precisely the failure the well-known index exists to prevent.

### Expressing multiple versions of the same IG

The well-known index uses separate keys (`davinci_crd_hook#1.1` and
`davinci_crd_hook#2.0`) to express that a payer supports two versions of the
same IG simultaneously. In Plan-Net, this is expressed by publishing **two
separate `Endpoint` resources**, each with its own `endpoint-usecase.standard`
URI carrying a distinct version. No structural change to Plan-Net is needed —
but the pattern must be **explicitly documented** in Plan-Net guidance and must
be testable, which requires `endpoint-usecase` to be MustSupport.

### Proposed Plan-Net changes

**P6 — Promote `endpoint-usecase` to MustSupport.**

This is the highest-leverage change in the endpoint layer. Once `endpoint-usecase`
is MustSupport, every conformant payer must populate it, every conformant
consumer must process it, and the NDH StructureMap can map it rather than drop
it. Without this change, the entire endpoint routing problem remains unsolved
in Plan-Net regardless of any other changes.

**P7 — Require `endpoint-usecase.standard` to carry a versioned IG URI.**

The `standard` sub-element of `endpoint-usecase` is a plain `uri`. Without
explicit guidance, payers will omit the version. A versioned URI (e.g.
`http://hl7.org/fhir/us/davinci-crd|2.0.0`) is what allows a consumer to
distinguish CRD 1.1 from CRD 2.0. This should be a **SHALL** requirement with
a computable invariant.

**P8 — Explicitly document the multiple-version Endpoint pattern.**

Add a guidance section to Plan-Net stating that when a payer supports multiple
versions of the same IG, each version is published as a separate `Endpoint`
resource with its own `endpoint-usecase.standard` value. This is a
documentation and testability change, not a structural one.

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
| P6 | `plannet-Endpoint` | `extension:endpoint-usecase` | Promote to MustSupport |
| P7 | `plannet-Endpoint` | `endpoint-usecase.standard` | Require versioned IG URI (SHALL + invariant) |
| P8 | Plan-Net guidance | (documentation) | Document multiple-version Endpoint pattern |

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

3. **What is the canonical form for a versioned IG URI in `endpoint-usecase.standard`?**
   This needs agreement across Da Vinci work groups before an invariant can
   be written for P7.

4. **How are non-FHIR URLs (payer homepage, documentation page) best expressed
   in Plan-Net?** The `rest-non-fhir` connection type exists, but using it for
   a plain informational website needs clarification. If there is no clean fit,
   these fields remain in the well-known index.
