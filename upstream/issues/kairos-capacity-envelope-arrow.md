<!-- GENERATED — DO NOT EDIT; run `make generate`. -->
# feat: Aggregate capacity envelopes and implied resource requirements without person-level records.

## Problem

This reusable interface is currently implemented by a project-local oracle. It belongs upstream,
but the downstream open pipeline must continue to work before any upstream release.

## Proposed interface

Aggregate capacity envelopes and implied resource requirements without person-level records.

Operations:

- `capacity_envelope`
- `implied_capacity`
- `outage_sensitivity`

Input contract: aggregate arrivals, pathway resource use, resource envelope, site state, and period.

Output contract: implied capacity, utilisation envelope, unmet aggregate demand, and queue summary.

## Compatibility fixture

- Deterministic Parquet fixture: `upstream/fixtures/kairos.parquet`
- Local compatibility oracle: `src/closer_to_whom/capacity.py`
- Pinned repository identity: `fae901558f07b7b717a676adbafbe2cdc78dea1c` on `main`

## Acceptance

- `uv run pytest -q tests/unit/test_simulation_metrics.py::test_equity_and_capacity`
- Fixture round-trips with the canonical Arrow/Parquet schema and exact library identity.
- The upstream integration remains optional and the local oracle passes when it is unavailable.
- No project-specific policy semantics, person-level data, credentials, or licensed payloads enter the fixture.

## Handoff boundary

This is a patch-ready proposal, not evidence of an upstream issue, merge, release, suitability assessment,
security review, licence permission, endorsement, or execution of upstream code.
