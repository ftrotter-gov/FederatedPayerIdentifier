# ![BETA](https://img.shields.io/badge/BETA-red) Federated Payer Identifier (FPI) Prototype

The Federated Payer Identifier prototype is a "rough consensus and working
code" proposal that enables United States healthcare payers to self-enumerate.
It provides a consistent payer identity that can be connected to insurance
plans, public interoperability endpoints, and other payer identifiers.

This is an early prototype. Its formats and processes may change as the
National Provider and Payer Directory (NPD) evolves. Within the prototype,
this repository is the trusted working copy and the anticipated NPD role is to
republish accepted content. That operational role does not mean that the NPD
selects or generates a payer's FPI.

## Identity and authority model

An FPI is self-issued by a payer. The payer chooses a UUID and, once that FPI
is registered, CMS enforces its use.

The identity boundary is the legal payer entity that holds the relevant
insurance assets and liability for a set of beneficiaries. A legal payer
entity should have one FPI in relation to one liability and beneficiary set.

Ownership alone does not collapse multiple payer entities into one FPI.
Insurance structures can include a payer that owns another payer, several
nested levels of payer ownership, and payers that insure payer risk through
insurance or reinsurance arrangements. Each entity's actual insurance assets,
liabilities, and beneficiary obligations—not the ownership chain by itself—
determine the FPI boundary. Modeling those complex relationships is future
work.

A payer may choose either:

* a generated UUID using UUIDv1, UUIDv4, UUIDv6, UUIDv7, or UUIDv8; or
* a deterministic UUIDv5 based on an identifier selected by that payer.

No source identifier is universally preferred. FPIs generated from different
source identifiers are not expected to converge. Deterministic generation is
a convenience for the payer, not a central entity-resolution mechanism. See
[Generating Federated Payer Identifiers](GeneratingFederatedPayerIdentifiers.md)
for the supported generation procedure.

## Technical components

* [Federated Payer Identifier generation](GeneratingFederatedPayerIdentifiers.md)
  describes how a payer can create its FPI.
* [Payer well-known index format](WellKnownFileFormat.md) connects the FPI and
  payer or plan identifiers to the appropriate interoperability endpoints.
* [Payer index files](payer_index_files) are the repository's working copies.
  Git issues, pull requests, and history support review and correction.
* [All-at-once provider directory downloads](AllAtOnce.md) describes how a
  payer can publish Da Vinci Plan-Net data in bulk.
* [Future steps](FutureSteps.md) records validation, delegation, nested payer
  ownership, reinsurance, historical, and governance capabilities that are
  deliberately outside the current prototype.

## Problems addressed here

* **Identify payer organizations** at the legal entity and liability boundary.
* **Represent a payer's plans** and the identifiers used to discover them.
* **Associate endpoints with plans** that share the same endpoint set.
* **Support plan discovery** from insurance-card and consumer-facing terms.
* **Crosswalk payer identifiers** without asserting that those identifiers
  are interchangeable or must generate the same FPI.
* **Supply NPD-ready payer directory data** informed by the
  [FAST NDH implementation guide](https://build.fhir.org/ig/HL7/fhir-us-ndh/en/).
