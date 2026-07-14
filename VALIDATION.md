# Local verification report

- Profile: `local`
- Revision: `a66ac81237d4783d97b3c2e3dbf76c0e23a4dce7`
- Dirty at start: `True`
- Overall required-gate status: **passed**
- Passed: 27; failed: 0; skipped: 0

A skipped optional capability is not represented as a pass. Scientific publication still requires the data, evidence, clinical, equity, and governance freezes listed in `docs/publication/manuscript-freeze.md`.

| Gate | Required | Status | Seconds | Evidence |
|---|---:|---|---:|---|
| `compile` | yes | **passed** | 1.316 | `release/receipts/logs/compile.log` |
| `generated-files` | yes | **passed** | 3.805 | `release/receipts/logs/generated-files.log` |
| `lockfile-portability` | yes | **passed** | 0.478 | `release/receipts/logs/lockfile-portability.log` |
| `machine-readability` | yes | **passed** | 1.388 | `release/receipts/logs/machine-readability.log` |
| `model-contracts` | yes | **passed** | 1.094 | `release/receipts/logs/model-contracts.log` |
| `assumption-contract` | yes | **passed** | 0.507 | `release/receipts/logs/assumption-contract.log` |
| `source-registry` | yes | **passed** | 0.534 | `release/receipts/logs/source-registry.log` |
| `protocol-consistency` | yes | **passed** | 0.545 | `release/receipts/logs/protocol-consistency.log` |
| `claim-boundaries` | yes | **passed** | 0.601 | `release/receipts/logs/claim-boundaries.log` |
| `privacy-and-licences` | yes | **passed** | 1.133 | `release/receipts/logs/privacy-and-licences.log` |
| `repository-hygiene` | yes | **passed** | 0.730 | `release/receipts/logs/repository-hygiene.log` |
| `workflow-structure` | yes | **passed** | 0.606 | `release/receipts/logs/workflow-structure.log` |
| `workflow-hardening` | yes | **passed** | 0.575 | `release/receipts/logs/workflow-hardening.log` |
| `version-consistency` | yes | **passed** | 0.441 | `release/receipts/logs/version-consistency.log` |
| `ruff` | yes | **passed** | 0.268 | `release/receipts/logs/ruff.log` |
| `ruff-format` | yes | **passed** | 0.298 | `release/receipts/logs/ruff-format.log` |
| `tests-coverage` | yes | **passed** | 43.073 | `release/receipts/logs/tests-coverage.log` |
| `mypy` | yes | **passed** | 1.583 | `release/receipts/logs/mypy.log` |
| `pyright` | yes | **passed** | 18.206 | `release/receipts/logs/pyright.log` |
| `codespell` | yes | **passed** | 1.505 | `release/receipts/logs/codespell.log` |
| `docs` | yes | **passed** | 6.162 | `release/receipts/logs/docs.log` |
| `package-build` | yes | **passed** | 30.324 | `release/receipts/logs/package-build.log` |
| `package-smoke` | yes | **passed** | 10.232 | `release/receipts/logs/package-smoke.log` |
| `deterministic-demo` | yes | **passed** | 5.375 | `release/receipts/logs/deterministic-demo.log` |
| `publication-readiness` | yes | **passed** | 0.543 | `release/receipts/logs/publication-readiness.log` |
| `secret-scan` | yes | **passed** | 1.017 | `release/receipts/logs/secret-scan.log` |
| `jax-differential` | no | **passed** | 4.025 | `release/receipts/logs/jax-differential.log` |

## Interpretation

This receipt verifies the repository and synthetic development harness in the recorded environment. It does not validate actual New Zealand service capability, patient journeys, confidential capacity, treatment uptake, waiting time, or clinical outcomes.
