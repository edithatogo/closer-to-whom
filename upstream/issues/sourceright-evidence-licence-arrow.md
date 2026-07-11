# feat: evidence grades, licence states, and Arrow claim graph export

## Problem

Policy models need a machine-readable claim–source graph that distinguishes evidentiary strength from access and redistribution permission.

## Proposed interface

Add typed `Claim`, `Source`, `EvidenceLink`, `LicenceState`, and `EvidenceGrade` records; validate fail-closed redistribution; export/import Arrow tables with schema/version fingerprints; expose unresolved and superseded claims.

## Acceptance

- deterministic Arrow round trip;
- duplicate and dangling-link validation;
- only explicitly open sources may be marked redistributable by default;
- claim status and evidence grade remain separate;
- property tests and migration notes.

## Project oracle

`src/closer_to_whom/integrations/sourceright_adapter.py` and `data/public/source-registry.yaml`.
