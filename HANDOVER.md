# Local handover

## 1. Clone and verify

```bash
git clone <repository-or-bundle> closer-to-whom
cd closer-to-whom
git verify-tag v0.2.0-handover || true
sha256sum -c release/SHA256SUMS 2>/dev/null || true
```

The source ZIP intentionally excludes `.git`, caches, environments, raw licensed data, and generated secrets. The Git bundle preserves history and tags.

## 2. Toolchain

Preferred local stack:

- Python 3.14 is the sole supported runtime and release path;
- `uv` for deterministic Python environments;
- Rust stable for `healthpoint-rs` integration tests;
- Mojo nightly or the current stable release only inside the canary job until promoted;
- Docker/BuildKit for the Hugging Face Space and reproducibility checks;
- optional Quarto for manuscript rendering.

Bootstrap:

```bash
./scripts/bootstrap-local.sh
uv run closer-to-whom doctor --strict
make check
```

## 3. Secrets and external services

Copy `.env.example` to `.env`; never commit `.env`. The open model needs no secrets. Optional variables are used only for licensed Healthpoint access, GitHub automation, OIA submission, map-tile services, and external routing. CI should use environment-scoped, least-privilege secrets.

## 4. Immediate execution order

1. Complete the nationwide service census using `docs/methods/service-census.md`.
2. Record each claim in `data/public/source-registry.yaml` and materialise the facility registry.
3. Acquire and licence-check public population, boundary, NZDep, GCH, incidence, cost, parking, fare, and treatment-policy inputs.
4. Freeze clinical pathway definitions with clinical review.
5. Run national routing in tiled, cached batches and preserve engine/version fingerprints.
6. Calibrate aggregate expected demand to public totals.
7. Execute baseline, structural, DSA, PSA, optimisation, MCDA, and VOI pipelines.
8. Run the publication gate and generate the NZMJ artefact set.

## 5. Boundaries requiring local action

This environment cannot responsibly complete live service-census adjudication, licensed Healthpoint acquisition, authenticated GitHub administration, OIA submission, or clinical/Māori governance review. The repository contains workflows, schemas, checklists, and fail-closed adapters for those steps.

## 6. Release gate

```bash
make release-gate
```

The gate performs formatting, linting, typing, tests, coverage, property and contract checks, reproducibility, generated-file drift, licence and privacy checks, dashboard smoke tests, package build/install, SBOM generation, vulnerability scanning where available, and release-manifest generation. Optional-tool absence is reported distinctly from failure.

## 7. Dashboard deployment

The Space consumes precomputed aggregate result cubes only:

```bash
docker build -f containers/huggingface.Dockerfile -t closer-to-whom-space .
docker run --rm -p 7860:7860 closer-to-whom-space
```

Set the Hugging Face Space SDK to Docker. Never mount raw or licensed source payloads into the public image.

## 8. Local integration receipt (2026-07-12)

The accompanying handover archive was verified against `MANIFEST.json`, the
embedded Git bundle, and all 283 source-file SHA-256 records. Its history was
imported into the project-local branch
`codex/closer-to-whom-integration-20260712`; the parent OneDrive worktree was
left untouched.

The local release profile passed with 79 tests, 89.56% branch-aware coverage,
strict documentation, package smoke, deterministic synthetic demonstration,
clean-room installation, JAX differential testing, contract checks, governance
checks, and secret scanning. This is software and synthetic-fixture evidence
only. The national service census, licensing adjudication, clinical review,
Māori/equity governance, ethics-scope determination, and authenticated upstream
GitHub work remain open.
