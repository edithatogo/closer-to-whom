# Local verification report

- Profile: `local`
- Revision: `cd39816a398abde0b24b4a9b5468c6f91b2f552d`
- Dirty at start: `True`
- Overall required-gate status: **passed**
- Passed: 27; failed: 0; skipped: 0

A skipped optional capability is not represented as a pass. Scientific publication still requires the data, evidence, clinical, equity, and governance freezes listed in `docs/publication/manuscript-freeze.md`.

| Gate | Required | Status | Seconds | Evidence |
|---|---:|---|---:|---|
| `compile` | yes | **passed** | 0.878 | `release/receipts/logs/compile.log` |
| `generated-files` | yes | **passed** | 2.566 | `release/receipts/logs/generated-files.log` |
| `lockfile-portability` | yes | **passed** | 0.369 | `release/receipts/logs/lockfile-portability.log` |
| `machine-readability` | yes | **passed** | 0.913 | `release/receipts/logs/machine-readability.log` |
| `model-contracts` | yes | **passed** | 1.026 | `release/receipts/logs/model-contracts.log` |
| `assumption-contract` | yes | **passed** | 0.899 | `release/receipts/logs/assumption-contract.log` |
| `source-registry` | yes | **passed** | 0.755 | `release/receipts/logs/source-registry.log` |
| `protocol-consistency` | yes | **passed** | 0.813 | `release/receipts/logs/protocol-consistency.log` |
| `claim-boundaries` | yes | **passed** | 0.594 | `release/receipts/logs/claim-boundaries.log` |
| `privacy-and-licences` | yes | **passed** | 0.829 | `release/receipts/logs/privacy-and-licences.log` |
| `repository-hygiene` | yes | **passed** | 0.464 | `release/receipts/logs/repository-hygiene.log` |
| `workflow-structure` | yes | **passed** | 0.454 | `release/receipts/logs/workflow-structure.log` |
| `workflow-hardening` | yes | **passed** | 0.399 | `release/receipts/logs/workflow-hardening.log` |
| `version-consistency` | yes | **passed** | 0.421 | `release/receipts/logs/version-consistency.log` |
| `ruff` | yes | **passed** | 0.261 | `release/receipts/logs/ruff.log` |
| `ruff-format` | yes | **passed** | 0.242 | `release/receipts/logs/ruff-format.log` |
| `tests-coverage` | yes | **passed** | 18.733 | `release/receipts/logs/tests-coverage.log` |
| `mypy` | yes | **passed** | 0.785 | `release/receipts/logs/mypy.log` |
| `pyright` | yes | **passed** | 11.616 | `release/receipts/logs/pyright.log` |
| `codespell` | yes | **passed** | 0.877 | `release/receipts/logs/codespell.log` |
| `docs` | yes | **passed** | 3.475 | `release/receipts/logs/docs.log` |
| `package-build` | yes | **passed** | 29.811 | `release/receipts/logs/package-build.log` |
| `package-smoke` | yes | **passed** | 9.035 | `release/receipts/logs/package-smoke.log` |
| `deterministic-demo` | yes | **passed** | 5.036 | `release/receipts/logs/deterministic-demo.log` |
| `publication-readiness` | yes | **passed** | 0.313 | `release/receipts/logs/publication-readiness.log` |
| `secret-scan` | yes | **passed** | 0.620 | `release/receipts/logs/secret-scan.log` |
| `jax-differential` | no | **passed** | 1.990 | `release/receipts/logs/jax-differential.log` |

## Interpretation

This receipt verifies the repository and synthetic development harness in the recorded environment. It does not validate actual New Zealand service capability, patient journeys, confidential capacity, treatment uptake, waiting time, or clinical outcomes.
