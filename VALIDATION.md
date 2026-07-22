# Local verification report

- Profile: `push`
- Revision: `14041846010dfbcd3fa53274edd9fb7f424cf485`
- Dirty at start: `False`
- Overall required-gate status: **passed**
- Passed: 17; failed: 0; skipped: 0

A skipped optional capability is not represented as a pass. Scientific publication still requires the data, evidence, clinical, equity, and governance freezes listed in `docs/publication/manuscript-freeze.md`.

| Gate | Required | Status | Seconds | Evidence |
|---|---:|---|---:|---|
| `compile` | yes | **passed** | 0.799 | `release/receipts/logs/compile.log` |
| `generated-files` | yes | **passed** | 4.027 | `release/receipts/logs/generated-files.log` |
| `lockfile-portability` | yes | **passed** | 0.309 | `release/receipts/logs/lockfile-portability.log` |
| `machine-readability` | yes | **passed** | 0.846 | `release/receipts/logs/machine-readability.log` |
| `model-contracts` | yes | **passed** | 0.716 | `release/receipts/logs/model-contracts.log` |
| `assumption-contract` | yes | **passed** | 0.310 | `release/receipts/logs/assumption-contract.log` |
| `source-registry` | yes | **passed** | 0.318 | `release/receipts/logs/source-registry.log` |
| `protocol-consistency` | yes | **passed** | 0.287 | `release/receipts/logs/protocol-consistency.log` |
| `claim-boundaries` | yes | **passed** | 0.318 | `release/receipts/logs/claim-boundaries.log` |
| `privacy-and-licences` | yes | **passed** | 0.558 | `release/receipts/logs/privacy-and-licences.log` |
| `repository-hygiene` | yes | **passed** | 0.347 | `release/receipts/logs/repository-hygiene.log` |
| `workflow-structure` | yes | **passed** | 0.301 | `release/receipts/logs/workflow-structure.log` |
| `workflow-hardening` | yes | **passed** | 0.308 | `release/receipts/logs/workflow-hardening.log` |
| `version-consistency` | yes | **passed** | 0.285 | `release/receipts/logs/version-consistency.log` |
| `ruff` | yes | **passed** | 0.435 | `release/receipts/logs/ruff.log` |
| `ruff-format` | yes | **passed** | 0.194 | `release/receipts/logs/ruff-format.log` |
| `tests-fast` | yes | **passed** | 50.517 | `release/receipts/logs/tests-fast.log` |

## Interpretation

This receipt verifies the repository and synthetic development harness in the recorded environment. It does not validate actual New Zealand service capability, patient journeys, confidential capacity, treatment uptake, waiting time, or clinical outcomes.
