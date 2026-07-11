# Conductor

Conductor is the repository's machine-readable execution and handover system. `project.yaml` defines the product; `state.yaml` records current state; `task-graph.json` defines dependencies; each track contains acceptance criteria and verification; receipts capture completed evidence.

A track may be `planned`, `active`, `blocked`, `completed`, or `superseded`. A completed track is not inferred from prose: it requires a receipt and the acceptance checks named by the track.
