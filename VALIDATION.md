# Local verification report

- Profile: `push`
- Revision: `e1d718d28c5eea542173891975ffdfad423c2c2b`
- Dirty at start: `False`
- Overall required-gate status: **passed**
- Passed: 17; failed: 0; skipped: 0

A skipped optional capability is not represented as a pass. Scientific publication still requires the data, evidence, clinical, equity, and governance freezes listed in `docs/publication/manuscript-freeze.md`.

| Gate | Required | Status | Seconds | Evidence |
|---|---:|---|---:|---|
| `compile` | yes | **passed** | 4.106 | `release/receipts/logs/compile.log` |
| `generated-files` | yes | **passed** | 7.708 | `release/receipts/logs/generated-files.log` |
| `lockfile-portability` | yes | **passed** | 1.135 | `release/receipts/logs/lockfile-portability.log` |
| `machine-readability` | yes | **passed** | 2.536 | `release/receipts/logs/machine-readability.log` |
| `model-contracts` | yes | **passed** | 4.646 | `release/receipts/logs/model-contracts.log` |
| `assumption-contract` | yes | **passed** | 0.744 | `release/receipts/logs/assumption-contract.log` |
| `source-registry` | yes | **passed** | 1.728 | `release/receipts/logs/source-registry.log` |
| `protocol-consistency` | yes | **passed** | 1.268 | `release/receipts/logs/protocol-consistency.log` |
| `claim-boundaries` | yes | **passed** | 0.910 | `release/receipts/logs/claim-boundaries.log` |
| `privacy-and-licences` | yes | **passed** | 1.676 | `release/receipts/logs/privacy-and-licences.log` |
| `repository-hygiene` | yes | **passed** | 1.579 | `release/receipts/logs/repository-hygiene.log` |
| `workflow-structure` | yes | **passed** | 2.398 | `release/receipts/logs/workflow-structure.log` |
| `workflow-hardening` | yes | **passed** | 1.749 | `release/receipts/logs/workflow-hardening.log` |
| `version-consistency` | yes | **passed** | 2.381 | `release/receipts/logs/version-consistency.log` |
| `ruff` | yes | **passed** | 4.252 | `release/receipts/logs/ruff.log` |
| `ruff-format` | yes | **passed** | 0.774 | `release/receipts/logs/ruff-format.log` |
| `tests-fast` | yes | **passed** | 145.283 | `release/receipts/logs/tests-fast.log` |

## Interpretation

This receipt verifies the repository and synthetic development harness in the recorded environment. It does not validate actual New Zealand service capability, patient journeys, confidential capacity, treatment uptake, waiting time, or clinical outcomes.
