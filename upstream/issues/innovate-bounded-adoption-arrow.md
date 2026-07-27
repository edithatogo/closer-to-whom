<!-- GENERATED — DO NOT EDIT; run `make generate`. -->
# feat: Bounded aggregate adoption trajectories with deterministic Arrow exchange.

## Problem

This reusable interface is currently implemented by a project-local oracle. It belongs upstream,
but the downstream open pipeline must continue to work before any upstream release.

## Proposed interface

Bounded aggregate adoption trajectories with deterministic Arrow exchange.

Operations:

- `logistic_adoption`
- `adoption_draws`
- `export_trajectory`

Input contract: time, floor, ceiling, midpoint, steepness, group, and parameter draw.

Output contract: adoption fraction constrained to the closed interval zero to one.

## Compatibility fixture

- Deterministic Parquet fixture: `upstream/fixtures/innovate.parquet`
- Local compatibility oracle: `src/closer_to_whom/integrations/adoption.py`
- Pinned repository identity: `339931e8cdd105a71ab30f334eaf7ab4a2939e21` on `main`

## Acceptance

- `uv run pytest -q tests/unit/test_validation_integrations.py::test_adoption_curve_and_capabilities`
- Fixture round-trips with the canonical Arrow/Parquet schema and exact library identity.
- The upstream integration remains optional and the local oracle passes when it is unavailable.
- No project-specific policy semantics, person-level data, credentials, or licensed payloads enter the fixture.

## Handoff boundary

This is a patch-ready proposal, not evidence of an upstream issue, merge, release, suitability assessment,
security review, licence permission, endorsement, or execution of upstream code.
