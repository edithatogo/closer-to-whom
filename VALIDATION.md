# Local verification report

- Profile: `push`
- Revision: `2ada1ff01a82216f98d94c1ff09c2153a3e7aab5`
- Dirty at start: `False`
- Overall required-gate status: **passed**
- Passed: 17; failed: 0; skipped: 0

A skipped optional capability is not represented as a pass. Scientific publication still requires the data, evidence, clinical, equity, and governance freezes listed in `docs/publication/manuscript-freeze.md`.

| Gate | Required | Status | Seconds | Evidence |
|---|---:|---|---:|---|
| `compile` | yes | **passed** | 6.215 | `release/receipts/logs/compile.log` |
| `generated-files` | yes | **passed** | 15.855 | `release/receipts/logs/generated-files.log` |
| `lockfile-portability` | yes | **passed** | 2.889 | `release/receipts/logs/lockfile-portability.log` |
| `machine-readability` | yes | **passed** | 10.942 | `release/receipts/logs/machine-readability.log` |
| `model-contracts` | yes | **passed** | 11.549 | `release/receipts/logs/model-contracts.log` |
| `assumption-contract` | yes | **passed** | 2.980 | `release/receipts/logs/assumption-contract.log` |
| `source-registry` | yes | **passed** | 3.210 | `release/receipts/logs/source-registry.log` |
| `protocol-consistency` | yes | **passed** | 3.548 | `release/receipts/logs/protocol-consistency.log` |
| `claim-boundaries` | yes | **passed** | 1.633 | `release/receipts/logs/claim-boundaries.log` |
| `privacy-and-licences` | yes | **passed** | 4.785 | `release/receipts/logs/privacy-and-licences.log` |
| `repository-hygiene` | yes | **passed** | 3.849 | `release/receipts/logs/repository-hygiene.log` |
| `workflow-structure` | yes | **passed** | 5.860 | `release/receipts/logs/workflow-structure.log` |
| `workflow-hardening` | yes | **passed** | 6.227 | `release/receipts/logs/workflow-hardening.log` |
| `version-consistency` | yes | **passed** | 4.568 | `release/receipts/logs/version-consistency.log` |
| `ruff` | yes | **passed** | 1.511 | `release/receipts/logs/ruff.log` |
| `ruff-format` | yes | **passed** | 1.538 | `release/receipts/logs/ruff-format.log` |
| `tests-fast` | yes | **passed** | 88.809 | `release/receipts/logs/tests-fast.log` |

## Interpretation

This receipt verifies the repository and synthetic development harness in the recorded environment. It does not validate actual New Zealand service capability, patient journeys, confidential capacity, treatment uptake, waiting time, or clinical outcomes.
