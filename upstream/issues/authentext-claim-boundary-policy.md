<!-- GENERATED — DO NOT EDIT; run `make generate`. -->
# feat: Declarative claim-boundary lint with machine-readable diagnostics.

## Problem

This reusable interface is currently implemented by a project-local oracle. It belongs upstream,
but the downstream open pipeline must continue to work before any upstream release.

## Proposed interface

Declarative claim-boundary lint with machine-readable diagnostics.

Operations:

- `load_policy`
- `lint_claims`
- `emit_diagnostics`

Input contract: scoped text plus prohibited and required phrase policy.

Output contract: deterministic line diagnostics in JSON or SARIF-compatible records.

## Compatibility fixture

- Deterministic Parquet fixture: `upstream/fixtures/authentext.parquet`
- Local compatibility oracle: `scripts/check_claim_boundaries.py`
- Pinned repository identity: `7f70dad5b6deab1af92faf037ef2638e7f3aea05` on `main`

## Acceptance

- `uv run pytest -q tests/contract/test_repository_contracts.py::test_claim_boundaries`
- Fixture round-trips with the canonical Arrow/Parquet schema and exact library identity.
- The upstream integration remains optional and the local oracle passes when it is unavailable.
- No project-specific policy semantics, person-level data, credentials, or licensed payloads enter the fixture.

## Handoff boundary

This is a patch-ready proposal, not evidence of an upstream issue, merge, release, suitability assessment,
security review, licence permission, endorsement, or execution of upstream code.
