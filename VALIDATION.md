# Validation receipt

**Release candidate:** `v0.2.0-handover`

**Validation date:** 2026-07-11

**Scope:** open, aggregate, synthetic-fixture research software only

This receipt records checks executed in the handover container. It is not clinical,
operational, service-capability, or policy validation. The nationwide public-service
census, public-data calibration, clinical review, Māori and equity governance review,
and ethics-scope documentation remain publication prerequisites.

## Passing gates

| Gate | Result |
|---|---|
| Locked dependency graph | `uv.lock` resolved for 145 package records and checked as portable: public PyPI endpoints only, no embedded credentials or private-index URLs |
| Formatting | Ruff format check passed across 102 Python files |
| Lint | Ruff passed |
| Static typing | strict Mypy passed across 42 source files; Pyright passed with 0 errors and 0 warnings |
| Tests | 79 passed |
| Branch-aware coverage | 89.56%; release floor 89% |
| Repository contracts | JSON/YAML parse, Arrow/JSON schemas, generated-file drift, assumption coverage, source registry, protocol, version and workflow checks passed |
| Governance boundaries | claim, privacy, licence, secret and public-source checks passed |
| Documentation | MkDocs strict build passed |
| Distribution build | wheel and source distribution built successfully |
| Wheel smoke test | built wheel installed with its resolved dependency graph into a fresh `uv` environment and the CLI schema registry executed successfully |
| Reproducibility | deterministic synthetic nationwide demonstration check passed |
| JAX/XLA differential test | 512 draws × 256 cells passed against the NumPy oracle; maximum relative error `2.143837233407802e-07` |
| Complexity budget | passed |

The test suite generated 100 model-result rows, 10 scenario-summary rows, 66
implied-capacity rows, 30 ethnicity-equity rows, 30 rurality-equity rows, and 12
better/worse rows from synthetic fixtures. All manifests label those outputs as
synthetic demonstrations.

## Toolchain observed

- CPython 3.13.5
- Polars 1.42.1
- PyArrow 25.0.0
- JAX/JAXlib 0.10.2
- Ruff 0.15.21
- Mypy 2.2.0
- Pyright 1.1.411
- Git 2.47.3
- uv 0.11.28

## Environment-limited gates

Docker, Quarto, Cargo/Rust, and Mojo were not installed in this container. Their
workflows, canaries, language-neutral Arrow contracts, numerical-equivalence gates,
and promotion criteria are included but were not represented as locally passed.
The container's direct public PyPI DNS access was restricted; the committed lock was
therefore independently normalised and checked to contain only public PyPI endpoints,
while package execution used the environment's package mirror.

## Claim boundary

The verified artefact is a research-software scaffold and synthetic nationwide
demonstration. It does not establish actual New Zealand treatment locations,
treatment volumes, patient travel, waiting times, existing capacity, uptake,
preferences, clinical outcomes, or cost-effectiveness.
