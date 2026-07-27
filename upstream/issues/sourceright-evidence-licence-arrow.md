<!-- GENERATED — DO NOT EDIT; run `make generate`. -->
# feat: Typed claim-source links with evidence and fail-closed licence state.

## Problem

This reusable interface is currently implemented by a project-local oracle. It belongs upstream,
but the downstream open pipeline must continue to work before any upstream release.

## Proposed interface

Typed claim-source links with evidence and fail-closed licence state.

Operations:

- `validate_claim_graph`
- `unresolved_claims`
- `export_claim_graph`

Input contract: claim_id, claim text, source identifiers, evidence grade, licence state, and claim status.

Output contract: validated Arrow claim graph plus unresolved and superseded claim sets.

## Compatibility fixture

- Deterministic Parquet fixture: `upstream/fixtures/sourceright.parquet`
- Local compatibility oracle: `src/closer_to_whom/integrations/sourceright_adapter.py`
- Pinned repository identity: `dde39b3bb334f79f12e395a5317b21e036336bdd` on `main`

## Acceptance

- `uv run pytest -q tests/unit/test_validation_integrations.py::test_claim_adapter_and_voiage_fallback`
- Fixture round-trips with the canonical Arrow/Parquet schema and exact library identity.
- The upstream integration remains optional and the local oracle passes when it is unavailable.
- No project-specific policy semantics, person-level data, credentials, or licensed payloads enter the fixture.

## Handoff boundary

This is a patch-ready proposal, not evidence of an upstream issue, merge, release, suitability assessment,
security review, licence permission, endorsement, or execution of upstream code.
