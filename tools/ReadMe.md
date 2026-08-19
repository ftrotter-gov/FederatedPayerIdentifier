# Tools

This directory contains scripts for generating, enriching, cleaning, and
reporting on payer well-known index files.

The repository does not yet contain the planned formal semantic validator.
Current scripts perform task-specific checks only and must not be described as
validating the complete well-known format. See
[Future Steps](../FutureSteps.md).

## Lifecycle expectations

General-purpose seeders create records with `is_seeded: true` and must not
overwrite a payer directory after its record is curated. A person or curation
process must set `is_seeded` to `false` when enriching seed output.

Purpose-specific cleanup and enrichment tools should preserve curated content
outside the fields they explicitly change. Git history is the current audit
and recovery mechanism. Future tooling should add dry runs, atomic writes or
backups, validation before replacement, and change summaries.

All deterministic FPI generation must use `FPI_maker_cli.py`; other tools must
import its functions rather than reimplementing UUID namespace logic.
