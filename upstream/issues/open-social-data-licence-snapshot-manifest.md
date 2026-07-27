<!-- GENERATED — DO NOT EDIT; run `make generate`. -->
# feat: Public-source snapshot manifests separating access, represented date, and redistribution.

## Problem

This reusable interface is currently implemented by a project-local oracle. It belongs upstream,
but the downstream open pipeline must continue to work before any upstream release.

## Proposed interface

Public-source snapshot manifests separating access, represented date, and redistribution.

Operations:

- `snapshot_source`
- `validate_licence`
- `materialisation_receipt`

Input contract: source identity, retrieval and represented dates, terms evidence, transform graph, and policy.

Output contract: checksummed Arrow or Parquet receipt with explicit public-private boundary.

## Compatibility fixture

- Deterministic Parquet fixture: `upstream/fixtures/open_social_data.parquet`
- Local compatibility oracle: `data/public/source-registry.yaml`
- Pinned repository identity: `29c8908267cbca47e91a6a93c9dceed1978b4a9e` on `main`

## Acceptance

- `uv run pytest -q tests/contract/test_repository_contracts.py::test_privacy_and_licences`
- Fixture round-trips with the canonical Arrow/Parquet schema and exact library identity.
- The upstream integration remains optional and the local oracle passes when it is unavailable.
- No project-specific policy semantics, person-level data, credentials, or licensed payloads enter the fixture.

## Handoff boundary

This is a patch-ready proposal, not evidence of an upstream issue, merge, release, suitability assessment,
security review, licence permission, endorsement, or execution of upstream code.
