# Handover release notes

## Version 0.2.0-handover

This release packages a nationwide, public-data, aggregate research-software scaffold
for modelling alternative anti-HER2 cancer-treatment service configurations in
Aotearoa New Zealand.

### Included

- initialised Git and Conductor project state, tracks, task graph, decisions,
  verification policy, and handover contract;
- public-source and licensing registries with fail-closed capability evidence;
- aggregate demand, routing, pathway, cost, equity, implied-capacity, optimisation,
  MCDA, uncertainty and value-of-information modules;
- IV trastuzumab, standalone subcutaneous trastuzumab, PHESGO, satellite, community,
  home/mobile, hybrid, travel-support, and outage scenarios;
- Polars/Arrow contracts and deterministic Parquet/IPC outputs;
- JAX/XLA acceleration with a NumPy oracle and differential test;
- a Mojo accelerator candidate with canary, parity, benchmark, and promotion gates;
- synthetic nationwide fixtures and tests only, with no patient or confidential data;
- a Hugging Face Docker Space scaffold consuming precomputed aggregate results;
- upstream-library issue, track, patch, and handoff material;
- NZMJ and decision-science manuscript scaffolds;
- CI/CD, dependency-lock portability, security, supply-chain, reproducibility,
  documentation, clean-room, and release workflows.

### Verification

See `VALIDATION.md`. The current environment passed formatting, lint, Mypy,
Pyright, 79 tests, an 89.56% branch-aware coverage gate, contract and governance
checks, strict documentation build, wheel/sdist build, isolated wheel smoke test,
deterministic reproducibility, and JAX differential testing.

### Local handover requirements

- install from the committed public `uv.lock` using
  `uv sync --locked --all-extras`;
- execute Docker, Rust and Mojo gates locally or in CI where those toolchains are
  available;
- complete and freeze the national public service census and licence adjudication;
- freeze public demand, clinical and cost inputs with appropriate review;
- obtain Māori/equity governance and ethics-scope documentation before publication.

### Claim boundary

No output in this release is an estimate of actual New Zealand service use, patient
journeys, existing capacity, waiting, preferences, outcomes, or cost-effectiveness.

## 2026-07-12 local integration

The handover ZIP was verified against its manifest, embedded Git bundle, and all
283 source checksums. The preserved history was imported into the project-local
branch `codex/closer-to-whom-integration-20260712` because the destination folder
was nested in an unrelated parent worktree.

The local release profile passed with 79 tests, 89.56% branch-aware coverage,
strict documentation, package smoke, deterministic synthetic demonstration,
contract and governance checks, secret scanning, clean-room installation, and JAX
differential testing. No candidate release tag was created because the complete
full profile was not completed within the local execution window. National
service-census, public-data, clinical, Māori/equity, ethics-scope, and licensing
gates remain open.
