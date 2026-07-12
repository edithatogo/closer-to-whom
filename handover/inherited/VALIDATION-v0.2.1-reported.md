# Validation receipt

**Release candidate:** `v0.3.0-handover`

**Validation date:** 2026-07-11

**Scope:** open, aggregate, public-data-compatible research software and synthetic fixtures only

This receipt records checks executed in the handover container. It is not clinical,
operational, service-capability, or policy validation. The nationwide public-service
census, public-data calibration, clinical review, Māori and equity governance review,
and ethics-scope documentation remain publication prerequisites.

## Passing gates

| Gate | Result |
|---|---|
| Locked dependency graph | `uv.lock` contains 142 package records and passed the portability gate: public PyPI endpoints only, with no embedded credentials or private-index URLs |
| Formatting | Ruff format check passed across 119 Python files |
| Lint and spelling | Ruff and codespell passed; generated documentation, build artefacts, caches, upstream patch worktrees, and environments are excluded explicitly |
| Dependency hygiene | Deptry passed with explicit ignores limited to documented optional backends, runner packages, and the self-referential `all` extra |
| Documentation coverage | Interrogate passed at 90.3% against a 90% floor |
| Dead-code scan | Vulture passed at 90% confidence |
| Static typing | Strict Mypy passed across 50 source files; Pyright passed with 0 errors and 0 warnings |
| Tests | 98 passed |
| Branch-aware coverage | 89.73%; release floor 89% |
| GitHub ecosystem census | 165 public repositories catalogued in profile order; 96 public forks identified; 137 repositories selected for bounded use; 18 core typed integrations; 8 cross-repository pipelines; 0 mandatory owner-repository runtime dependencies |
| Ecosystem safety | Every selected repository is mapped to a bounded pipeline; forks cannot be core or required runtime dependencies; workspace planning is non-executing; network and write operations require explicit opt-in |
| Machine-readable ecosystem exports | Deterministic CSV, Parquet, Arrow IPC, JSON, and generated Markdown/audit reports passed round-trip and cross-reference tests |
| Repository contracts | JSON/YAML parse, Arrow/JSON schemas, generated-file drift, assumption coverage, source registry, protocol, version, workflow, and ecosystem checks passed |
| Governance boundaries | Claim, privacy, licence, public-source, publication-readiness, and secret-scan checks passed |
| Documentation | MkDocs strict build passed |
| Distribution build | Wheel and source distribution built successfully as version 0.3.0 |
| Wheel smoke test | The built wheel installed with its resolved dependency graph into a fresh `uv` environment and the CLI schema registry executed successfully |
| SBOM | Deterministic CycloneDX 1.5-compatible inventory generated with 130 environment components and the application version derived from `pyproject.toml` |
| Reproducibility | Deterministic synthetic nationwide demonstration passed repeated-run checks |
| JAX/XLA differential test | 512 draws × 256 cells passed against the NumPy oracle; maximum relative error `2.143837233407802e-07` |
| Portable benchmark | Three synthetic national runs passed the 30-second budget; median `0.28216699599988715` seconds |
| Complexity and hygiene | Complexity-budget and repository-hygiene checks passed |

The synthetic demonstration generated 100 model-result rows, 10 scenario-summary
rows, 66 implied-capacity rows, 30 ethnicity-equity rows, 30 rurality-equity rows,
and 12 better/worse rows. Every manifest labels those outputs as synthetic
demonstrations.

## Public GitHub ecosystem boundary

The frozen catalogue covers the 165 repositories visible publicly under
`edithatogo` on 2026-07-11. It does not claim visibility into private repositories,
organisation-only repositories, deleted repositories, or repositories created after
the snapshot. Catalogue selection means that a repository has a bounded evidence,
method, interoperability, harness, publication, dissemination, or local-AI role. It
does not mean that all 137 selected repositories are installed, imported, executed,
API-compatible, or licensed for redistribution.

The optional workspace materialiser is plan-only by default. Even when explicitly
enabled, it performs shallow source checkout only and does not install, import, build,
test, or execute external repository code.

## Toolchain observed

- CPython 3.13.5
- Polars 1.42.1
- PyArrow 25.0.0
- JAX/JAXlib 0.10.2
- Ruff 0.15.21
- Mypy 2.2.0
- Pyright 1.1.411
- Git 2.47.3
- uv 0.10.0

## Environment-limited gates

Docker, Quarto, Cargo/Rust, Mojo, Bandit, and `pip-audit` were not installed in this
container. Their workflows, canaries, language-neutral Arrow contracts,
numerical-equivalence gates, supply-chain controls, and promotion criteria are
included but are not represented as locally passed.

The container could not resolve public PyPI for an online vulnerability audit.
The committed lock was therefore independently normalised and checked to contain
only public PyPI endpoints, while package execution used the environment's package
mirror. An isolated wheel smoke installation passed; the broader clean-room script
timed out during dependency installation and is not claimed as passed.

No authenticated GitHub mutation was performed. Upstream issue files and patches are
local handover material until remote publication and replay against current upstream
default branches are independently confirmed.

## Claim boundary

The verified artefact is a research-software scaffold, public-source evidence system,
and synthetic nationwide demonstration. It does not establish actual New Zealand
treatment locations, treatment volumes, patient travel, waiting times, existing
capacity, uptake, preferences, clinical outcomes, causal effects, or
cost-effectiveness.
