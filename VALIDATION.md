# Local verification report

- Profile: `local`
- Revision: `c5c6a4919eb33bf36f782f36cbcef638ebefc2f2`
- Dirty at start: `False`
- Overall required-gate status: **passed**
- Passed: 27; failed: 0; skipped: 0

A skipped optional capability is not represented as a pass. Scientific publication still requires the data, evidence, clinical, equity, and governance freezes listed in `docs/publication/manuscript-freeze.md`.

| Gate | Required | Status | Seconds | Evidence |
|---|---:|---|---:|---|
| `compile` | yes | **passed** | 0.417 | `release/receipts/logs/compile.log` |
| `generated-files` | yes | **passed** | 1.578 | `release/receipts/logs/generated-files.log` |
| `lockfile-portability` | yes | **passed** | 0.328 | `release/receipts/logs/lockfile-portability.log` |
| `machine-readability` | yes | **passed** | 0.651 | `release/receipts/logs/machine-readability.log` |
| `model-contracts` | yes | **passed** | 0.616 | `release/receipts/logs/model-contracts.log` |
| `assumption-contract` | yes | **passed** | 0.251 | `release/receipts/logs/assumption-contract.log` |
| `source-registry` | yes | **passed** | 0.246 | `release/receipts/logs/source-registry.log` |
| `protocol-consistency` | yes | **passed** | 0.259 | `release/receipts/logs/protocol-consistency.log` |
| `claim-boundaries` | yes | **passed** | 0.215 | `release/receipts/logs/claim-boundaries.log` |
| `privacy-and-licences` | yes | **passed** | 0.366 | `release/receipts/logs/privacy-and-licences.log` |
| `repository-hygiene` | yes | **passed** | 0.275 | `release/receipts/logs/repository-hygiene.log` |
| `workflow-structure` | yes | **passed** | 0.261 | `release/receipts/logs/workflow-structure.log` |
| `workflow-hardening` | yes | **passed** | 0.281 | `release/receipts/logs/workflow-hardening.log` |
| `version-consistency` | yes | **passed** | 0.250 | `release/receipts/logs/version-consistency.log` |
| `ruff` | yes | **passed** | 0.153 | `release/receipts/logs/ruff.log` |
| `ruff-format` | yes | **passed** | 0.142 | `release/receipts/logs/ruff-format.log` |
| `tests-coverage` | yes | **passed** | 18.023 | `release/receipts/logs/tests-coverage.log` |
| `mypy` | yes | **passed** | 0.675 | `release/receipts/logs/mypy.log` |
| `pyright` | yes | **passed** | 8.880 | `release/receipts/logs/pyright.log` |
| `codespell` | yes | **passed** | 0.612 | `release/receipts/logs/codespell.log` |
| `docs` | yes | **passed** | 2.982 | `release/receipts/logs/docs.log` |
| `package-build` | yes | **passed** | 11.625 | `release/receipts/logs/package-build.log` |
| `package-smoke` | yes | **passed** | 6.143 | `release/receipts/logs/package-smoke.log` |
| `deterministic-demo` | yes | **passed** | 2.276 | `release/receipts/logs/deterministic-demo.log` |
| `publication-readiness` | yes | **passed** | 0.254 | `release/receipts/logs/publication-readiness.log` |
| `secret-scan` | yes | **passed** | 0.441 | `release/receipts/logs/secret-scan.log` |
| `jax-differential` | no | **passed** | 1.772 | `release/receipts/logs/jax-differential.log` |

## Interpretation

This receipt verifies the repository and synthetic development harness in the recorded environment. It does not validate actual New Zealand service capability, patient journeys, confidential capacity, treatment uptake, waiting time, or clinical outcomes.
