# Closer to whom?

[![CI](https://github.com/edithatogo/closer-to-whom/actions/workflows/ci.yml/badge.svg)](https://github.com/edithatogo/closer-to-whom/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/edithatogo/closer-to-whom/branch/main/graph/badge.svg)](https://codecov.io/gh/edithatogo/closer-to-whom)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A public-data, aggregate geospatial policy simulation of alternative anti-HER2 cancer-treatment service configurations across Aotearoa New Zealand.

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
