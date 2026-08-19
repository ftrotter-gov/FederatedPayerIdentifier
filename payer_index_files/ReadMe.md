# Payer Well-Known Index Files

This directory contains the trusted working copies of payer well-known index
files. Files may begin as generated seed data and then be corrected or enriched
through curation. Accepted repository content is intended to be republished by
the National Provider and Payer Directory (NPD).

## Seeded and curated records

The `is_seeded` property records the lifecycle state:

* `true` means that the file remains automated seed output.
* `false` means that a person or curation process has reviewed or enriched it.

Changing a seeded file through curation must also change `is_seeded` to
`false`. General-purpose seeders must not overwrite a curated payer directory.
Other automated curation tools must preserve curated facts unless their
documented purpose explicitly calls for changing those facts. Git history is
the current audit and snapshot mechanism.

Seeded FPIs based on normalized payer names are a temporary data-loading
compromise. Payer names are not the permanent FPI identity boundary, and
duplicate seed files are not automatically merged merely because their names
match. The payer ultimately self-issues the FPI for the legal entity holding
the relevant assets and liability for its beneficiary population.

See [the format reference](../WellKnownFileFormat.md) for file semantics and
[Future Steps](../FutureSteps.md) for deferred validation and lifecycle work.
