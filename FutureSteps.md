# Future Steps

This document records capabilities that are important to the Federated Payer
Identifier (FPI) design but are deliberately outside the current prototype.
Listing an item here does not commit the project to a particular implementation.

## Semantic validation

The project expects to add a Python validator rather than a JSON Schema. JSON
syntax and structural checks are only part of the requirement. The validator
will eventually need to evaluate domain-specific behavior, including:

* whether an endpoint implements the protocol and FHIR version named by its key;
* whether a URL is a service base, resource, capability statement, download,
  documentation page, or human lookup page appropriate to that field;
* which properties are required and which may be null;
* whether null, omitted, unsupported, and not-yet-discovered capabilities need
  distinct treatment;
* whether identifier systems, identifier values, and UUID source metadata agree;
* whether plan, payer, coverage-area, and endpoint relationships are plausible;
* whether a record marked as curated satisfies stronger requirements than seed
  data; and
* whether report generation preserves rather than obscures validation status.

The validator should produce specific, actionable diagnostics. Validation rules
must be documented alongside the implementation as they are adopted.


## Historical identifiers and effective periods

The current prototype primarily represents current payer and routing
identifiers. Future work may model historical values, effective and expiration
dates, replacement relationships, provenance, and verification status. Git
history is the current record-level snapshot mechanism; no separate snapshot
protocol is presently planned.

## Delegation between FPIs

The prototype does not currently let one FPI delegate authority or operations
to another FPI. Future work should determine whether delegation is needed,
which responsibilities can be delegated, how the relationship is authorized,
and how consumers avoid confusing delegation with a transfer of liability.

## Payers Who Own Payers Who Own Payers

Insurance ownership and risk structures can have several distinct layers. A
payer may own another payer, that payer may own another payer, and payers may
insure payer risk through insurance or reinsurance arrangements. An owning
company may also hold insurance assets and liabilities of its own.

The current prototype identifies the legal payer entity at the point where the
relevant insurance assets, liability, and beneficiary obligations are held. It
does not yet represent the relationships among all entities in a nested payer
ownership chain or distinguish ownership, direct insurance liability,
reinsurance, risk transfer, and administrative operations.

Future work should define how these relationships are represented without
collapsing legally or financially distinct payers into one FPI. It should also
address how liability moves through insurance and reinsurance arrangements and
how consumers determine which entity is responsible for a beneficiary set.

## Payers with no enumerated identifier

An FPI must be derived from a legacy identifier the payer already holds in one
of the enumerated payer identifier systems; a payer may not mint a UUID of its
own. See
[Deprecating Newly Generated Identifiers](AI_Instructions/DeprecatingNewIdentifiers.md).

The current answer for a payer that holds no enumerated identifier is to submit
a pull request adding its identifier system to
`reference_data/current_payer_identification_systems.json`. Future work should
decide whether that is sufficient in practice, or whether some assignment
mechanism is needed for payers that genuinely hold no suitable legacy
identifier in any recognized system.

## Domain authority and outsourced FHIR services

The well-known index is intended to bridge a payer-controlled publication
location to FHIR endpoints that may be hosted on an outsourced vendor's domain.
Domain names will therefore be a major trust signal, but a simple same-domain
rule would reject legitimate vendor arrangements.

Future work should define payer-domain control, vendor delegation, redirect
handling, endpoint ownership changes, and evidence retained during review. The
initial implementation does not require signatures or automated TLS/domain
control proofs.

## Curated-record safeguards

Automation that touches curated files should eventually support documented
merge rules, validation before replacement, dry-run output, backups or atomic
writes, and clear change summaries. The project also needs an explicit policy
for which generated facts can be refreshed without erasing aliases, lookup
URLs, endpoint annotations, or other curated content.

## Sandbox endpoint scope

`plan_endpoints_sandbox` is currently defined only at the `plan_group` level,
mirroring where `plan_endpoints` lives. Two related scopes remain unresolved:

* a payer-wide sandbox, which would belong alongside the FPI identifier entry
  rather than being repeated in every `plan_group`; and
* a plan-specific sandbox, for a payer whose test environment differs per plan.

Most payers appear to operate a single sandbox tier for all of their plans, so
repeating the same block in each `plan_group` may prove redundant in practice.
Future work should decide whether a payer-level declaration is worth adding and,
if so, how a `plan_group` entry overrides or supplements it.

The semantic validator will also need rules for this object: whether a sandbox
url must be reachable, whether it must differ from its production counterpart,
and whether a sandbox key with no production counterpart is a warning or an
accepted state.

## Plan years and publication history

Current Medicare Advantage seed data is source-year-specific, while the index
format does not yet define durable plan identity or effective periods. Future
work should decide whether plan membership is a dated assertion, how annual
changes are represented, and when Git history is insufficient for consumers.

## Documentation review findings

The repository-wide review that produced this document identified several
themes for ongoing cleanup:

* keep payer-selected legacy enumeration separate from CMS enforcement and NPD
  republication;
* do not describe registration as generating a canonical replacement FPI;
* keep temporary legal-name seeding separate from the permanent identity model;
* distinguish payer, plan, routing, and source identifiers;
* distinguish endpoint protocol/version coordinates from index-file versioning;
* distinguish payer-controlled publication from vendor-hosted services;
* document seeded-to-curated safeguards consistently across tools; and
* treat current report anomalies as validation inputs where coverage semantics
  remain undefined, rather than automatically declaring them source defects.
  