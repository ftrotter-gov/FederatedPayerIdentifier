Payer Identifier Types
=============

This is a list of existing identity enumeration systems that exist for Payers. 
Current CMS plans intend for the industry to use "payer-selected legacy enumeration", which means that payers can choose any of these existing enumeration systems to anchor their FPI. A payer does not mint a new identifier of its own; it selects a legacy identifier it already holds. 
These will be encorporated into some kind of referencable thing in the NDH FHIR IG (there are several possibilities for this, 
including a ValueSet, so that they can be referenced as "systems" in the identifiers section for a payer Organization FHIR record.

Plan Identifier Types
=============

`current_plan_identification_systems.json` is the companion list for *plans* rather than payer legal entities.
Where a payer identifier system enumerates the contracting legal entity, a plan identifier system enumerates one specific insurance product offered by that entity.
These are the systems allowed in the `system` member of a plan identifier inside a plan group (see the Plan Identifiers section of FederatedPayerIdentifierSpecification.md).
Each entry carries the same fields as the payer list, plus `parent_payer_identification_system`, which points at the payer identifier system the plan system hangs off of.
Every plan identifier in a well-known file also carries `parent_fpi` (the FPI of the owning payer entity) and `f_plan_id` (the Federated Plan Identifier), regardless of which plan identifier system its `system`/`value` pair comes from.
