# Agent operating contract

## Mission

Advance a reproducible, public-data policy model without crossing its evidence, privacy, clinical, or licensing boundaries.

## Mandatory read order

1. `conductor/project.yaml`
2. `conductor/state.yaml`
3. `conductor/task-graph.json`
4. `conductor/decisions/decision-log.yaml`
5. `assumptions/assumptions.yaml`
6. `data/public/source-registry.yaml`
7. active track specification and verification contract

## Non-negotiable rules

- Never add individual, confidential, de-identified-but-non-public, or row-level health-service data.
- Never label an aggregate expected-demand row as a patient.
- Treat undocumented service capability as `unknown`, not `absent`.
- Keep clinical eligibility and safety as hard constraints, never compensatory MCDA criteria.
- Keep parameter, structural, spatial, and decision uncertainty distinguishable.
- Every externally derived parameter or service claim needs a source record, retrieval date, licence state, and evidence grade.
- Do not commit live Healthpoint payloads. The adapter must fail closed without an explicit licence grant.
- Do not make operational or clinical claims from synthetic fixtures.
- Update the assumptions registry, decision log, tests, and documentation with every model change.
- Run `make check` before committing and `make release-gate` before a release candidate.

## Change protocol

1. Select or create a Conductor track.
2. Write acceptance criteria and verification evidence before implementation.
3. Make the smallest coherent commit.
4. Add unit, property, contract, integration, and regression tests appropriate to the risk.
5. Generate a receipt with hashes and tool versions.
6. Record any unresolved uncertainty or follow-up issue.

## Upstream libraries

Prefer adapters and thin compatibility layers. Reusable functionality that belongs in `sourceright`, `authentext`, `innovate`, `voiage`, `kairos`, `mars`, `open_social_data`, `healthpoint-rs`, or `fyi-cli` must be represented by:

- a local Conductor dependency track;
- a GitHub issue body in `upstream/issues/`;
- a tested patch or implementation branch where feasible;
- a compatibility fallback so this repository remains reproducible before upstream release.

## Generated files

Files marked with `GENERATED — DO NOT EDIT` must be regenerated through the documented command. CI checks drift.
