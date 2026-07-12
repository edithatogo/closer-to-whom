# Local verification report

- Profile: `local`
- Revision: `ec79bb97054f8ed26d9155c0f35f218fdfb42fd7`
- Dirty at start: `True`
- Overall required-gate status: **passed**
- Passed: 27; failed: 0; skipped: 0

A skipped optional capability is not represented as a pass. Scientific publication still requires the data, evidence, clinical, equity, and governance freezes listed in `docs/publication/manuscript-freeze.md`.

| Gate | Required | Status | Seconds | Evidence |
|---|---:|---|---:|---|
| `compile` | yes | **passed** | 0.450 | `release/receipts/logs/compile.log` |
| `generated-files` | yes | **passed** | 1.403 | `release/receipts/logs/generated-files.log` |
| `lockfile-portability` | yes | **passed** | 0.334 | `release/receipts/logs/lockfile-portability.log` |
| `machine-readability` | yes | **passed** | 0.677 | `release/receipts/logs/machine-readability.log` |
| `model-contracts` | yes | **passed** | 0.593 | `release/receipts/logs/model-contracts.log` |
| `assumption-contract` | yes | **passed** | 0.262 | `release/receipts/logs/assumption-contract.log` |
| `source-registry` | yes | **passed** | 0.279 | `release/receipts/logs/source-registry.log` |
| `protocol-consistency` | yes | **passed** | 0.274 | `release/receipts/logs/protocol-consistency.log` |
| `claim-boundaries` | yes | **passed** | 0.225 | `release/receipts/logs/claim-boundaries.log` |
| `privacy-and-licences` | yes | **passed** | 0.363 | `release/receipts/logs/privacy-and-licences.log` |
| `repository-hygiene` | yes | **passed** | 0.268 | `release/receipts/logs/repository-hygiene.log` |
| `workflow-structure` | yes | **passed** | 0.267 | `release/receipts/logs/workflow-structure.log` |
| `workflow-hardening` | yes | **passed** | 0.282 | `release/receipts/logs/workflow-hardening.log` |
| `version-consistency` | yes | **passed** | 0.262 | `release/receipts/logs/version-consistency.log` |
| `ruff` | yes | **passed** | 0.145 | `release/receipts/logs/ruff.log` |
| `ruff-format` | yes | **passed** | 0.131 | `release/receipts/logs/ruff-format.log` |
| `tests-coverage` | yes | **passed** | 17.314 | `release/receipts/logs/tests-coverage.log` |
| `mypy` | yes | **passed** | 0.926 | `release/receipts/logs/mypy.log` |
| `pyright` | yes | **passed** | 8.861 | `release/receipts/logs/pyright.log` |
| `codespell` | yes | **passed** | 0.597 | `release/receipts/logs/codespell.log` |
| `docs` | yes | **passed** | 2.966 | `release/receipts/logs/docs.log` |
| `package-build` | yes | **passed** | 12.252 | `release/receipts/logs/package-build.log` |
| `package-smoke` | yes | **passed** | 6.489 | `release/receipts/logs/package-smoke.log` |
| `deterministic-demo` | yes | **passed** | 2.321 | `release/receipts/logs/deterministic-demo.log` |
| `publication-readiness` | yes | **passed** | 0.257 | `release/receipts/logs/publication-readiness.log` |
| `secret-scan` | yes | **passed** | 0.450 | `release/receipts/logs/secret-scan.log` |
| `jax-differential` | no | **passed** | 1.732 | `release/receipts/logs/jax-differential.log` |

## Interpretation

This receipt verifies the repository and synthetic development harness in the recorded environment. It does not validate actual New Zealand service capability, patient journeys, confidential capacity, treatment uptake, waiting time, or clinical outcomes.
