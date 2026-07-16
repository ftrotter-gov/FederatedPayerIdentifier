# ![BETA](https://img.shields.io/badge/BETA-red) Federated Payer Identifier (FPI) Prototype

The Federated Payer Identifier prototype is a "rough consensus working code" proposal that enables healthcare payers in the United States to self-enumerate in support of a National Provider and Payer Directory. Its purpose is to improve interoperability by providing a consistent way to identify payers and facilitate discovery of their public interoperability data.

This repository contains an early prototype and should not be considered a formal or permanent identification system. As the National Provider and Payer Directory evolves, this approach may be substantially revised or replaced by a more mature solution. Accordingly, the contents of this repository should be viewed as exploratory and illustrative rather than authoritative.


## The Technical Components: 

* [Federated Payer Identifier (FPI)](GeneratingFederatedPayerIdentifiers.md): A methodology that allows Payers to generate their own ids
* [Payer well-known endpoint file format definition](WellKnownFileFormat.md): A file that leverages the FPI in order to enable lookups against Payers and Insurance Plans, in order to find the correct endpoints
* [Mirroring Payer well-known endpoint files here](payer_index_files): in order to use git-tooling (i.e. pull requests and tickets etc). In order to triage Data Quality Act corrections from payers and the public to ensure that the payer endpoint data is correct.

## The problems addressesed here

* **Uniquely identify payer organizations** so that each healthcare payer corporate entity can be consistently and correctly represented.

* **Represent a payer's insurance plans** by allowing each payer to express the set of insurance plans it offers.

* **Associate interoperability endpoints with plans** by publishing the relevant FHIR endpoints and other interoperability metadata for each insurance plan.

* **Support user-friendly plan discovery** by mapping payer and plan identifiers to the terminology commonly available to patients, such as information printed on health insurance cards or other consumer-facing plan names used during shopping and enrollment.

* **Crosswalk payer identifiers** by maintaining mappings between the various payer identifier systems so that searches can reliably resolve to the correct payer and associated interoperability resources.

* **Provide the details needed for a National Payer Directory** ensure that all of the above can be done in a manner that can be consumable by the NPD (https://directory.cms.gov/) according to the standards of the NDH FAST FHIR IG (https://build.fhir.org/ig/HL7/fhir-us-ndh/en/)
