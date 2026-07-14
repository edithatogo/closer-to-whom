# Local verification report

- Profile: `local`
- Revision: `288ba353a86337950f92a889d549b1fdf860e80d`
- Dirty at start: `True`
- Overall required-gate status: **passed**
- Passed: 27; failed: 0; skipped: 0

A skipped optional capability is not represented as a pass. Scientific publication still requires the data, evidence, clinical, equity, and governance freezes listed in `docs/publication/manuscript-freeze.md`.

| Gate | Required | Status | Seconds | Evidence |
|---|---:|---|---:|---|
| `compile` | yes | **passed** | 1.042 | `release/receipts/logs/compile.log` |
| `generated-files` | yes | **passed** | 2.637 | `release/receipts/logs/generated-files.log` |
| `lockfile-portability` | yes | **passed** | 0.427 | `release/receipts/logs/lockfile-portability.log` |
| `machine-readability` | yes | **passed** | 1.215 | `release/receipts/logs/machine-readability.log` |
| `model-contracts` | yes | **passed** | 1.230 | `release/receipts/logs/model-contracts.log` |
| `assumption-contract` | yes | **passed** | 0.432 | `release/receipts/logs/assumption-contract.log` |
| `source-registry` | yes | **passed** | 0.441 | `release/receipts/logs/source-registry.log` |
| `protocol-consistency` | yes | **passed** | 0.435 | `release/receipts/logs/protocol-consistency.log` |
| `claim-boundaries` | yes | **passed** | 0.366 | `release/receipts/logs/claim-boundaries.log` |
| `privacy-and-licences` | yes | **passed** | 0.695 | `release/receipts/logs/privacy-and-licences.log` |
| `repository-hygiene` | yes | **passed** | 0.578 | `release/receipts/logs/repository-hygiene.log` |
| `workflow-structure` | yes | **passed** | 0.738 | `release/receipts/logs/workflow-structure.log` |
| `workflow-hardening` | yes | **passed** | 0.676 | `release/receipts/logs/workflow-hardening.log` |
| `version-consistency` | yes | **passed** | 0.692 | `release/receipts/logs/version-consistency.log` |
| `ruff` | yes | **passed** | 0.307 | `release/receipts/logs/ruff.log` |
| `ruff-format` | yes | **passed** | 0.252 | `release/receipts/logs/ruff-format.log` |
| `tests-coverage` | yes | **passed** | 36.511 | `release/receipts/logs/tests-coverage.log` |
| `mypy` | yes | **passed** | 1.009 | `release/receipts/logs/mypy.log` |
| `pyright` | yes | **passed** | 22.837 | `release/receipts/logs/pyright.log` |
| `codespell` | yes | **passed** | 9.587 | `release/receipts/logs/codespell.log` |
| `docs` | yes | **passed** | 7.111 | `release/receipts/logs/docs.log` |
| `package-build` | yes | **passed** | 32.711 | `release/receipts/logs/package-build.log` |
| `package-smoke` | yes | **passed** | 15.842 | `release/receipts/logs/package-smoke.log` |
| `deterministic-demo` | yes | **passed** | 5.707 | `release/receipts/logs/deterministic-demo.log` |
| `publication-readiness` | yes | **passed** | 0.427 | `release/receipts/logs/publication-readiness.log` |
| `secret-scan` | yes | **passed** | 0.781 | `release/receipts/logs/secret-scan.log` |
| `jax-differential` | no | **passed** | 10.215 | `release/receipts/logs/jax-differential.log` |

## Interpretation

This receipt verifies the repository and synthetic development harness in the recorded environment. It does not validate actual New Zealand service capability, patient journeys, confidential capacity, treatment uptake, waiting time, or clinical outcomes.
