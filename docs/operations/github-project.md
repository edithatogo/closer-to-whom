# GitHub project and assurance controls

The public [Closer to whom Conductor Roadmap](https://github.com/users/edithatogo/projects/25)
is the GitHub coordination layer for the local Conductor control plane.

## Hierarchy

Parent issues represent the nine Conductor workstreams, including the five original external
blockers and the four downstream dependency-gated tracks. Native GitHub subissues represent
their executable tasks. Pull request [#8](https://github.com/edithatogo/closer-to-whom/pull/8)
contains the merged first implementation slice. Residual operational and security work is tracked
as labelled action issues #31-#33 and included in the same Project. The machine-readable mapping is
`conductor/github-project.yaml`.

Local `conductor/state.yaml`, `conductor/task-graph.json`, track files, and receipts remain the
detailed source of truth. GitHub status is coordination evidence, not scientific evidence.

## Repository controls

The repository uses the active `main-high-assurance` ruleset. It blocks branch deletion and
non-fast-forward updates, requires pull requests, stale-review dismissal when reviews exist,
conversation resolution, and the CI/security check set. It intentionally requires zero
approving reviews and no Code Owner or last-push approval: this is a sole-developer code
harness. Repository merges are squash-only and merged branches are deleted automatically.
GitHub Code Quality rules are not enabled because the account does not expose that service; the
required `full` CI job still enforces static quality checks, the 89% branch-coverage floor, and
uploads the Cobertura report as an auditable artifact.

Dependabot security updates, secret scanning, and push protection are enabled. GitHub reports
non-provider secret patterns and validity checks as unavailable/disabled for this repository/account;
that residual control gap remains explicit rather than being represented as enabled.
GitHub Discussions are enabled for repository-level questions and decisions.

All workflow action references are pinned to verified immutable commit SHAs. Workflow permissions are
least-privilege by default, with security-event, OIDC, and attestation permissions scoped to the jobs
that require them. Docker/dashboard jobs do not receive package-write permission unless a future
publishing workflow explicitly needs it.
