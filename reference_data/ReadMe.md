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

Lines of Business
=============

`lines_of_business.json` enumerates the values allowed in the required root-level `line_of_business` member of a well-known index file (WK-155).

Line of business is the axis along which payer endpoints most often diverge, because payers frequently engage different subcontractors to handle claims and interoperability for each. Declaring it inside the file means the repository directory layout is *derived from* the tag rather than carrying meaning of its own: tooling can treat the corpus as a flat set of files and recover the intended placement from `line_of_business`. Each entry's `directory_name` records that correspondence.

Each entry also carries `default_fhir_product_type`, the `InsurancePlan.type` code suggested when compiling the file into NDH FHIR resources, together with `default_fhir_product_type_is_exact` and `fhir_product_type_notes`. Line of business is coarser than the HL7 `insurance-product-type` code system, so only `healthcare_marketplace_plans` maps exactly. `ERISA_plans` and `other` carry a `null` default because no suitable code exists or because the tag is too coarse to choose among several; those files need an explicit product type before they can produce a conforming NDH `InsurancePlan`. See [FPI_WellKnown_To_NDH_FHIR_Map.md](../FPI_WellKnown_To_NDH_FHIR_Map.md).
