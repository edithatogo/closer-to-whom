# Closer to whom?

[![CI](https://github.com/edithatogo/closer-to-whom/actions/workflows/ci.yml/badge.svg)](https://github.com/edithatogo/closer-to-whom/actions/workflows/ci.yml)
[![Security and supply chain](https://github.com/edithatogo/closer-to-whom/actions/workflows/security.yml/badge.svg)](https://github.com/edithatogo/closer-to-whom/actions/workflows/security.yml)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/edithatogo/closer-to-whom/badge)](https://securityscorecards.dev/viewer/?uri=github.com/edithatogo/closer-to-whom)
[![Documentation](https://img.shields.io/badge/docs-MkDocs-526CFE)](https://edithatogo.github.io/closer-to-whom/)
[![Python](https://img.shields.io/badge/python-3.11--3.14-3776AB)](pyproject.toml)
[![codecov](https://codecov.io/gh/edithatogo/closer-to-whom/branch/main/graph/badge.svg)](https://codecov.io/gh/edithatogo/closer-to-whom)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A public-data, aggregate geospatial policy simulation of alternative anti-HER2 cancer-treatment service configurations across Aotearoa New Zealand.

## Assurance status

| Surface | Current state | Evidence |
|---|---|---|
| Community health | 100% | [GitHub community profile](https://github.com/edithatogo/closer-to-whom/community) |
| Automated quality | Passing on the protected PR path | [Actions](https://github.com/edithatogo/closer-to-whom/actions) |
| Security analysis | CodeQL, dependency audit, secret scanning, and push protection enabled | [`SECURITY.md`](SECURITY.md) |
| Scientific publication | Blocked pending external service, input, clinical, licensing, Māori/equity, and ethics receipts | [`data/public/publication-gate.yaml`](data/public/publication-gate.yaml) |

This is a high-assurance research-software repository, not a claim that the
underlying national evidence is complete. Synthetic fixtures validate software
behaviour only; they do not establish service capability, capacity, clinical
eligibility, patient outcomes, or publication readiness.

## Claim boundary

This repository estimates **potential geographic and economic accessibility** under explicit assumptions. It does not contain patient records, infer actual patient journeys, estimate observed waiting times or capacity, or claim causal effects on attendance, treatment completion, or clinical outcomes. Synthetic fixtures are demonstrations only.

## What is implemented

- nationwide, evidence-graded service-registry contracts;
- aggregate expected-demand cells rather than synthetic people;
- IV trastuzumab, subcutaneous trastuzumab, PHESGO, satellite, community, home/mobile, and hybrid scenarios;
- Polars and Arrow-first data flow with schema fingerprints;
- route-engine protocols and deterministic offline routing fixtures;
- patient, whānau, public-payer, provider, and societal travel-cost perspectives;
- distributional access and equity metrics;
- implied capacity, p-median, p-centre, maximal-coverage, and Pareto analysis;
- DSA, PSA, structural uncertainty, EVPI, EVPPI, EVSI, ENBS, and break-even research costs;
- MCDA and stochastic rank acceptability;
- JAX/XLA acceleration with a NumPy reference oracle and differential tests;
- a Mojo accelerator track with canary, numerical-equivalence, and promotion gates;
- an aggregate-only Hugging Face Docker Space;
- machine-readable assumptions, provenance, decisions, tracks, tasks, and release receipts.

## Quick start

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
