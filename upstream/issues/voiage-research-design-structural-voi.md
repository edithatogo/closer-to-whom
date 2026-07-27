<!-- GENERATED — DO NOT EDIT; run `make generate`. -->
# feat: Structural value-of-information calculations with an explicit scalar value function.

## Problem

This reusable interface is currently implemented by a project-local oracle. It belongs upstream,
but the downstream open pipeline must continue to work before any upstream release.

## Proposed interface

Structural value-of-information calculations with an explicit scalar value function.

Operations:

- `core_voi`
- `evppi`
- `evsi`
- `research_design_value`

Input contract: draw-by-option net value matrix, perspective, design, delay, and affected population.

Output contract: EVPI, EVPPI, EVSI, probability optimal, and break-even information value.

## Compatibility fixture

- Deterministic Parquet fixture: `upstream/fixtures/voiage.parquet`
- Local compatibility oracle: `src/closer_to_whom/integrations/voiage_adapter.py`
- Pinned repository identity: `ceefb5155217058a6e8a9b263960daa36e5bae64` on `main`

## Acceptance

- `uv run pytest -q tests/unit/test_optional_integrations.py::test_voiage_adapter_accepts_compatible_result_and_falls_back`
- Fixture round-trips with the canonical Arrow/Parquet schema and exact library identity.
- The upstream integration remains optional and the local oracle passes when it is unavailable.
- No project-specific policy semantics, person-level data, credentials, or licensed payloads enter the fixture.

## Handoff boundary

This is a patch-ready proposal, not evidence of an upstream issue, merge, release, suitability assessment,
security review, licence permission, endorsement, or execution of upstream code.
