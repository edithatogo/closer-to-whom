# Handover release notes

## Version 0.3.0-handover

This release extends the nationwide, public-data, aggregate anti-HER2 policy-simulation
scaffold with an exhaustive, machine-readable integration map for the public GitHub
ecosystem visible under `edithatogo` at the frozen 2026-07-11 snapshot.

## GitHub ecosystem integration

- catalogues all 165 publicly visible repositories in profile order;
- records the exact 96-repository public fork set;
- assigns all repositories a category, suitability tier, bounded role, integration
  mode, dependency policy, guardrails, and rationale;
- selects 137 suitable repositories for bounded evidence, policy, analytical,
  harness, publication, dissemination, or local-AI roles;
- maps every selected repository to at least one of 8 explicit cross-repository
  pipelines;
- implements 18 core typed integration contracts and local oracles;
- preserves zero mandatory runtime dependencies on owner repositories;
- prohibits forks from becoming core or required runtime dependencies;
- exports deterministic CSV, Parquet, Arrow IPC, JSON, and Markdown views;
- packages those views, provenance files, schemas, and internal checksums as a standalone ecosystem handover ZIP;
- provides a safe plan-only workspace materialiser and scheduled GitHub name/fork
  drift detection;
- records private and organisation-only repositories as outside the observable scope.

Catalogue inclusion is not installation. External repositories are never imported or
executed automatically, and cloning requires separate network and write opt-ins.

## Research implementation retained and expanded

- initialised Git and Conductor project state, dependency-aware tracks, task graph,
  decisions, verification policy, and handover contract;
- public-source and licensing registries with fail-closed capability evidence;
- aggregate demand, routing, pathway, cost, equity, implied-capacity, optimisation,
  MCDA, uncertainty, adoption, and value-of-information modules;
- IV trastuzumab, standalone subcutaneous trastuzumab, PHESGO, satellite, community,
  home/mobile, hybrid, travel-support, and outage scenarios;
- Polars/Arrow contracts and deterministic Parquet/IPC outputs;
- JAX/XLA acceleration with NumPy oracles and differential testing;
- a Mojo accelerator candidate with canary, parity, benchmark, and promotion gates;
- synthetic nationwide fixtures only, with no patient or confidential data;
- a Hugging Face Docker Space scaffold consuming precomputed aggregate results;
- local upstream-library issue, track, patch, and handoff material;
- NZMJ and decision-science manuscript scaffolds;
- CI/CD, dependency-lock portability, security, supply-chain, reproducibility,
  documentation, clean-room, and release workflows.

## Additional hardening in this release

- canonical release-version consistency now covers package metadata, protocol,
  assumptions, and Conductor state;
- the SBOM application version is derived from `pyproject.toml` rather than hard-coded;
- the lock-normalisation guard only rewrites a recognised transparent mirror shape and
  fails closed for unknown private indexes;
- Pyright resolves the committed local virtual-environment contract;
- codespell excludes generated and third-party artefacts explicitly;
- runtime thread and XLA resource envelopes prevent high-core-count oversubscription.

## Verification

See `VALIDATION.md`. The handover container passed formatting, Ruff, codespell,
strict Mypy, Pyright, dependency hygiene, 90.3% docstring coverage, dead-code scanning, 98 tests, the 89.73% branch-aware coverage gate, ecosystem and
machine-contract checks, governance gates, strict documentation build, wheel/sdist
build, isolated wheel smoke installation, deterministic reproducibility, portable
benchmarking, JAX differential testing, SBOM generation, and secret scanning.

Docker, Quarto, Cargo/Rust, Mojo, Bandit, and online `pip-audit` execution were not
available in the container; their CI gates remain included for local or hosted
execution.

## Local handover requirements

- verify checksums, clone the Git bundle, and inspect the annotated release tag;
- install from the committed public `uv.lock` using `uv sync --locked --all-extras`;
- run `make verify`, then the environment-dependent Docker, Rust, Mojo, Quarto, and
  security gates;
- run the public GitHub drift check before relying on the frozen 165-repository
  catalogue;
- replay optional upstream patches against current default branches before opening
  issues or pull requests;
- complete and freeze the national public service census and licence adjudication;
- freeze public demand, clinical, routing, and cost inputs with appropriate review;
- obtain Māori/equity governance and ethics-scope documentation before publication.

## Claim boundary

No output in this release is an estimate of actual New Zealand service use, patient
journeys, existing capacity, waiting, preferences, outcomes, causal effects, or
cost-effectiveness. The GitHub catalogue records bounded optional composition; it does
not certify every external repository's current compatibility, security, maintenance,
or redistribution licence.
