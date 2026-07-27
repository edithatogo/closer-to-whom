<!-- GENERATED — DO NOT EDIT; run `make generate`. -->
# feat: Surrogate diagnostics that fail closed when decision loss is not acceptable.

## Problem

This reusable interface is currently implemented by a project-local oracle. It belongs upstream,
but the downstream open pipeline must continue to work before any upstream release.

## Proposed interface

Surrogate diagnostics that fail closed when decision loss is not acceptable.

Operations:

- `fit_surrogate`
- `diagnose_surrogate`
- `compare_decision_loss`

Input contract: deterministic train-test partitions, features, exact outcomes, and promotion thresholds.

Output contract: calibration, residuals, extrapolation flags, and exact-versus-surrogate decision loss.

## Compatibility fixture

- Deterministic Parquet fixture: `upstream/fixtures/mars.parquet`
- Local compatibility oracle: `src/closer_to_whom/voi.py`
- Pinned repository identity: `cc17c8d632419c0f4a293ced1e785bd8c3e5bed6` on `main`

## Acceptance

- `uv run pytest -q tests/unit/test_voi.py::test_evppi_methods`
- Fixture round-trips with the canonical Arrow/Parquet schema and exact library identity.
- The upstream integration remains optional and the local oracle passes when it is unavailable.
- No project-specific policy semantics, person-level data, credentials, or licensed payloads enter the fixture.

## Handoff boundary

This is a patch-ready proposal, not evidence of an upstream issue, merge, release, suitability assessment,
security review, licence permission, endorsement, or execution of upstream code.
