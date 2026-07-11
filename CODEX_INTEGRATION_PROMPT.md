# Codex handover prompt — Closer to whom?

You are integrating the **Closer to whom?** public-data health-service policy simulation into a local Git repository. Preserve the research claim boundary and the existing Git history. Do not replace machine-readable contracts with prose.

## Inputs

You will receive one or both of:

- `closer-to-whom-v0.2.0-handover.bundle` — preferred; contains Git history and tags.
- `closer-to-whom-v0.2.0-handover.zip` — source snapshot without `.git`.

You may also receive `closer-to-whom-v0.2.0-handover-release-manifest.json` and `closer-to-whom-v0.2.0-handover-SHA256SUMS`.

## Non-negotiable research boundaries

1. Use only public, aggregate, non-identifiable inputs in the open pipeline.
2. Treat undocumented service capability as **unknown**, not absent.
3. Do not present synthetic fixtures as observed New Zealand services, capacity, demand, travel, patient behaviour, waiting time, adherence, or outcomes.
4. Healthpoint data are fail-closed unless local licence grants explicitly permit acquisition, analysis, repository redistribution, and public-dashboard use.
5. OIA requests through `fyi-cli` are optional evidence-development tools, never build dependencies.
6. Clinical safety and medicine eligibility are hard constraints and may not be traded away by optimisation or MCDA.
7. Any future microdata work requires a separate protocol, governance and ethics-scope assessment.
8. Keep Arrow/Parquet contracts language-neutral. Python/Polars is the reference pipeline; JAX/XLA, Mojo, Rust and Julia components must pass differential and contract tests before promotion.

## Preferred integration path: Git bundle

```bash
sha256sum -c closer-to-whom-v0.2.0-handover-SHA256SUMS

git clone closer-to-whom-v0.2.0-handover.bundle closer-to-whom
cd closer-to-whom
git bundle verify ../closer-to-whom-v0.2.0-handover.bundle
git verify-tag v0.2.0-handover || git show v0.2.0-handover
```

When integrating into an existing repository rather than cloning:

```bash
git remote add handover /absolute/path/closer-to-whom-v0.2.0-handover.bundle
git fetch handover 'refs/heads/*:refs/remotes/handover/*' 'refs/tags/*:refs/tags/*'
git switch -c integrate/closer-to-whom handover/main
```

Then use `git merge --no-ff`, `git subtree`, or a carefully reviewed path-level import according to the local repository architecture. Never squash away the handover history until the integration has been verified and attributed.

## ZIP fallback

```bash
unzip closer-to-whom-v0.2.0-handover.zip
cd closer-to-whom-v0.2.0-handover
git init -b main
git add .
git commit -m 'chore: import closer-to-whom v0.2.0 handover'
```

Record the source manifest and original SHA-256 in the import commit or an ADR.

## Required read order

1. `AGENTS.md`
2. `conductor/project.yaml`
3. `conductor/state.yaml`
4. `conductor/task-graph.json`
5. `protocol/protocol.yaml`
6. `protocol/claim-boundaries.yaml`
7. `assumptions/assumptions.yaml`
8. `data/public/source-registry.yaml`
9. `schemas/arrow/index.json`
10. `schemas/json/index.json`
11. `HANDOVER.md`
12. the active track under `conductor/tracks/`

## Local bootstrap and verification

Use Python 3.12 or 3.13 for the release path.

```bash
./scripts/bootstrap-local.sh
uv sync --locked --all-extras
uv run closer-to-whom doctor --strict
make check
```

Before publication-oriented work:

```bash
make verify
# Full optional local gate, including clean-room, benchmark and security checks:
make release-gate
```

Where a tool is unavailable, record **not run** separately from **failed**. Do not weaken a gate silently. Update the relevant Conductor task, decision log and verification receipt whenever a gate or contract changes.

## First implementation tasks

1. Validate the repository and regenerate schemas; commit any deterministic drift separately.
2. Complete the systematic nationwide public-source service census using the evidence-grade contract.
3. Populate public population, boundary, NZDep, GCH, incidence, travel-cost, parking, fare and medicine-policy inputs with source/licence receipts.
4. Freeze early and metastatic anti-HER2 pathways through clinical review.
5. Run national routing in tiled, cached batches with engine/version fingerprints.
6. Calibrate aggregate expected demand only to publicly reported totals.
7. Execute structural scenarios, DSA, PSA, optimisation, MCDA and VOI.
8. Use VOI/ENBS to determine whether an aggregate operational study or later microdata study is worth commissioning.
9. Deploy only precomputed aggregate result cubes to the Hugging Face Docker Space.
10. Keep the NZMJ manuscript clinically focused; place detailed optimisation, MCDA and VOI methods in the second paper and technical report.

## Upstream libraries

Review `upstream/registry.yaml`, issue drafts and handoff metadata. For functionality that belongs in `sourceright`, `authentext`, `innovate`, `voiage`, `kairos`, `mars`, `open_social_data`, or `healthpoint-rs`:

- open or reconcile a GitHub issue against the current upstream default branch;
- implement in an isolated worktree;
- add contract and compatibility tests;
- publish a draft PR only after replaying the patch against current upstream;
- pin the compatible upstream revision in the integration receipt;
- keep an in-repository fallback until the upstream release is available.

Do not claim that any issue, PR, merge or release exists unless verified against the live remote.

## Completion response

At the end, report:

- imported revision and tag;
- integration strategy and commits created;
- verification commands and exact results;
- generated artefacts and hashes;
- unresolved external dependencies;
- Conductor tracks advanced or blocked;
- any claim-boundary, licence, clinical or reproducibility concern.
