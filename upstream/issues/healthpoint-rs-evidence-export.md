<!-- GENERATED — DO NOT EDIT; run `make generate`. -->
# feat: Licensed capability-evidence export with separate local and publication grants.

## Problem

This reusable interface is currently implemented by a project-local oracle. It belongs upstream,
but the downstream open pipeline must continue to work before any upstream release.

## Proposed interface

Licensed capability-evidence export with separate local and publication grants.

Operations:

- `validate_licence_grant`
- `export_private_arrow`
- `validate_publication_boundary`

Input contract: service query, typed evidence fields, source time, and four explicit permission states.

Output contract: private Arrow evidence and licence receipt; public output only with explicit grants.

## Compatibility fixture

- Deterministic Parquet fixture: `upstream/fixtures/healthpoint-rs.parquet`
- Local compatibility oracle: `src/closer_to_whom/integrations/healthpoint.py`
- Pinned repository identity: `82c83b0b7bcac739ff143e730e20889d3919c880` on `main`

## Acceptance

- `uv run pytest -q tests/unit/test_optional_integrations.py::test_healthpoint_success_path_remains_private`
- `uv run pytest -q tests/unit/test_validation_integrations.py::test_healthpoint_fail_closed`
- Fixture round-trips with the canonical Arrow/Parquet schema and exact library identity.
- The upstream integration remains optional and the local oracle passes when it is unavailable.
- No project-specific policy semantics, person-level data, credentials, or licensed payloads enter the fixture.

## Handoff boundary

This is a patch-ready proposal, not evidence of an upstream issue, merge, release, suitability assessment,
security review, licence permission, endorsement, or execution of upstream code.
