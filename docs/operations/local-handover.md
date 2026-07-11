# Local handover runbook

## Golden path

```bash
git clone <bundle-or-remote> closer-to-whom
cd closer-to-whom
./scripts/bootstrap-local.sh
uv run python -m closer_to_whom doctor --json
uv run python scripts/release_gate.py --profile local
```

The bootstrap script does not fetch confidential data. It creates the locked environment, installs Git hooks, regenerates machine artefacts, runs the fast harness, and writes a local receipt.

## Capability tiers

- **Core:** Python, Polars, Arrow, deterministic synthetic model and documentation.
- **Acceleration:** JAX/XLA differential tests.
- **Optimisation:** HiGHS/OR-Tools and optional Julia/JuMP service through Arrow contracts.
- **Mojo:** optional canary and benchmark; never publication-critical until the same oracle, property, differential, and reproducibility gates pass.
- **Licensed source:** Healthpoint connector remains fail-closed until local credentials, licence evidence, and publication permissions are provided.

## First local tasks

1. Confirm the Conductor state and create a local worktree per active track.
2. Run `ctw doctor --json` and retain the receipt.
3. Replace synthetic fixtures only through source-registry entries and reviewed transformations.
4. Complete the national facility census before interpreting scenario outputs.
5. Open or update upstream library issues/PRs from `upstream/` after checking current remote state.
6. Configure repository rulesets, protected environments, trusted publishing, and Hugging Face secrets locally; credentials are never embedded in the repository.
