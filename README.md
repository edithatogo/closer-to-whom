# Closer to whom?

[![CI](https://github.com/edithatogo/closer-to-whom/actions/workflows/ci.yml/badge.svg)](https://github.com/edithatogo/closer-to-whom/actions/workflows/ci.yml)
[![Security and supply chain](https://github.com/edithatogo/closer-to-whom/actions/workflows/security.yml/badge.svg)](https://github.com/edithatogo/closer-to-whom/actions/workflows/security.yml)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/edithatogo/closer-to-whom/badge)](https://securityscorecards.dev/viewer/?uri=github.com/edithatogo/closer-to-whom)
[![Documentation](https://img.shields.io/badge/docs-MkDocs-526CFE)](https://edithatogo.github.io/closer-to-whom/)
[![Python](https://img.shields.io/badge/python-3.14-3776AB)](pyproject.toml)
[![codecov](https://codecov.io/gh/edithatogo/closer-to-whom/branch/main/graph/badge.svg)](https://codecov.io/gh/edithatogo/closer-to-whom)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A public-data, aggregate geospatial policy simulation of alternative anti-HER2 cancer-treatment service configurations across Aotearoa New Zealand.

## Assurance status

| Surface | Current state | Evidence |
|---|---|---|
| Community health | 100% | [GitHub community profile](https://github.com/edithatogo/closer-to-whom/community) |
| Automated quality | Passing on the protected PR path | [Actions](https://github.com/edithatogo/closer-to-whom/actions) |
| Security analysis | CodeQL, dependency audit, secret scanning, and push protection enabled | [`SECURITY.md`](SECURITY.md) |
| Public aggregate publication | Reviewed five-report payload published; manuscript and broader outcome tracks remain open | [`data/public/publication-gate.yaml`](data/public/publication-gate.yaml) |

This is a high-assurance research-software repository, not a claim that the
underlying national evidence is complete. Synthetic fixtures validate software
behaviour only; they do not establish service capability, capacity, clinical
eligibility, patient outcomes, or publication readiness.

## Claim boundary

This repository estimates **potential geographic and economic accessibility** under explicit assumptions. It does not contain patient records, infer actual patient journeys, estimate observed waiting times or capacity, or claim causal effects on attendance, treatment completion, or clinical outcomes. Synthetic fixtures are demonstrations only.

## What is implemented

- reusable pathway, equity, capacity, optimisation, uncertainty, value-of-information, MCDA, and acceleration library components;
- aggregate expected-demand cells rather than synthetic people;
- bounded national five-report candidate-network analysis with reviewed public aggregate inputs;
- Polars and Arrow-first data flow with schema fingerprints, plus deterministic routing fixtures;
- an aggregate-only free Hugging Face Static Space;
- machine-readable assumptions, provenance, decisions, tracks, tasks, and release receipts.

Reusable library components are not automatically materialized national findings. The current national payload does not estimate unsupported delivery-setting capability, observed capacity, full cost perspectives, empirical PSA, monetary VOI, or broader distributional outcomes. Those remain tracked deliverables.

## Quick start

The supported runtime is CPython **3.14** only. The committed `uv.lock` is the
dependency source of truth and is refreshed with compatible latest releases.

```bash
# Preferred
uv sync --locked --all-extras
uv run closer-to-whom doctor
uv run closer-to-whom demo --output artifacts/demo
uv run closer-to-whom verify --input-dir artifacts/demo --output artifacts/demo/validation.json

# Fast developer loop
make check

# Full publication gate
make release-gate
```

The demo writes only synthetic Arrow/Parquet/JSON outputs. See [`HANDOVER.md`](HANDOVER.md) for local setup, credential boundaries, source acquisition, and the next executable tasks.

## Documentation and coordination

- [Model card](docs/model-card.md) — scope, assumptions, and claim boundaries.
- [Methods](docs/methods/travel-and-costs.md) — travel, cost, optimisation, uncertainty, and resilience methods.
- [Operations](docs/operations/testing.md) — quality, security, reproducibility, and release gates.
- [GitHub Project](https://github.com/users/edithatogo/projects/25) — parent issues, subissues, blockers, and implementation status.
- [Contributing](CONTRIBUTING.md) and [security policy](SECURITY.md) — change and disclosure procedures.

## Repository operating model

Humans and agents should read, in order:

1. [`AGENTS.md`](AGENTS.md)
2. [`conductor/project.yaml`](conductor/project.yaml)
3. [`conductor/state.yaml`](conductor/state.yaml)
4. [`conductor/task-graph.json`](conductor/task-graph.json)
5. [`assumptions/assumptions.yaml`](assumptions/assumptions.yaml)
6. [`docs/model-card.md`](docs/model-card.md)
7. the active track under [`conductor/tracks`](conductor/tracks)

Machine-readable files are canonical until the publication freeze. Generated prose must be reproducible from them.

## Data policy

Only public, aggregate, non-confidential inputs are permitted in the open pipeline. Public accessibility and redistribution permission are separate checks. Healthpoint payloads are fail-closed and may not be committed or deployed unless the licence manifest explicitly permits both. OIA requests may improve public evidence but are not dependencies.

## Licence

Code is MIT licensed. Third-party data retain their own licences and are governed by `data/public/source-registry.yaml` and `data/public/licence-policy.yaml`.
