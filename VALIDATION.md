# Local verification report

- Profile: `local`
- Revision: `492a18cddf278547dfac423490ff5657b383e153`
- Dirty at start: `False`
- Overall required-gate status: **passed**
- Passed: 27; failed: 0; skipped: 0

A skipped optional capability is not represented as a pass. Scientific publication still requires the data, evidence, clinical, equity, and governance freezes listed in `docs/publication/manuscript-freeze.md`.

| Gate | Required | Status | Seconds | Evidence |
|---|---:|---|---:|---|
| `compile` | yes | **passed** | 7.008 | `release/receipts/logs/compile.log` |
| `generated-files` | yes | **passed** | 11.963 | `release/receipts/logs/generated-files.log` |
| `lockfile-portability` | yes | **passed** | 0.297 | `release/receipts/logs/lockfile-portability.log` |
| `machine-readability` | yes | **passed** | 6.135 | `release/receipts/logs/machine-readability.log` |
| `model-contracts` | yes | **passed** | 0.764 | `release/receipts/logs/model-contracts.log` |
| `assumption-contract` | yes | **passed** | 0.322 | `release/receipts/logs/assumption-contract.log` |
| `source-registry` | yes | **passed** | 0.308 | `release/receipts/logs/source-registry.log` |
| `protocol-consistency` | yes | **passed** | 0.292 | `release/receipts/logs/protocol-consistency.log` |
| `claim-boundaries` | yes | **passed** | 1.149 | `release/receipts/logs/claim-boundaries.log` |
| `privacy-and-licences` | yes | **passed** | 1.339 | `release/receipts/logs/privacy-and-licences.log` |
| `repository-hygiene` | yes | **passed** | 0.333 | `release/receipts/logs/repository-hygiene.log` |
| `workflow-structure` | yes | **passed** | 0.363 | `release/receipts/logs/workflow-structure.log` |
| `workflow-hardening` | yes | **passed** | 0.350 | `release/receipts/logs/workflow-hardening.log` |
| `version-consistency` | yes | **passed** | 0.316 | `release/receipts/logs/version-consistency.log` |
| `ruff` | yes | **passed** | 0.200 | `release/receipts/logs/ruff.log` |
| `ruff-format` | yes | **passed** | 0.198 | `release/receipts/logs/ruff-format.log` |
| `tests-coverage` | yes | **passed** | 95.705 | `release/receipts/logs/tests-coverage.log` |
| `mypy` | yes | **passed** | 16.349 | `release/receipts/logs/mypy.log` |
| `pyright` | yes | **passed** | 13.722 | `release/receipts/logs/pyright.log` |
| `codespell` | yes | **passed** | 1.229 | `release/receipts/logs/codespell.log` |
| `docs` | yes | **passed** | 10.509 | `release/receipts/logs/docs.log` |
| `package-build` | yes | **passed** | 27.042 | `release/receipts/logs/package-build.log` |
| `package-smoke` | yes | **passed** | 9.626 | `release/receipts/logs/package-smoke.log` |
| `deterministic-demo` | yes | **passed** | 2.758 | `release/receipts/logs/deterministic-demo.log` |
| `publication-readiness` | yes | **passed** | 0.356 | `release/receipts/logs/publication-readiness.log` |
| `secret-scan` | yes | **passed** | 0.611 | `release/receipts/logs/secret-scan.log` |
| `jax-differential` | no | **passed** | 2.713 | `release/receipts/logs/jax-differential.log` |

## Interpretation

This receipt verifies the repository and synthetic development harness in the recorded environment. It does not validate actual New Zealand service capability, patient journeys, confidential capacity, treatment uptake, waiting time, or clinical outcomes.
