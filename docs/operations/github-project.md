# GitHub project and assurance controls

The public [Closer to whom Conductor Roadmap](https://github.com/users/edithatogo/projects/25)
is the GitHub coordination layer for the local Conductor control plane.

## Hierarchy

Parent issues represent the nine Conductor workstreams, including the five original external
blockers and the four downstream dependency-gated tracks. Native GitHub subissues represent
their executable tasks. Pull request [#8](https://github.com/edithatogo/closer-to-whom/pull/8)
contains the first implementation slice. The machine-readable mapping is
`conductor/github-project.yaml`.

Local `conductor/state.yaml`, `conductor/task-graph.json`, track files, and receipts remain the
detailed source of truth. GitHub status is coordination evidence, not scientific evidence.

## Repository controls

The repository uses the active `main-high-assurance` ruleset. It blocks branch deletion and
non-fast-forward updates, requires pull requests, code-owner review, stale-review dismissal,
conversation resolution, and the CI/security check set. Repository merges are squash-only and
merged branches are deleted automatically.

Dependabot security updates, secret scanning, and push protection are enabled. GitHub reports
non-provider secret patterns and validity checks as unavailable/disabled for this repository/account;
that residual control gap remains explicit rather than being represented as enabled.
GitHub Discussions are enabled for repository-level questions and decisions.

All workflow action references are pinned to verified immutable commit SHAs. Workflow permissions are
least-privilege by default, with security-event, OIDC, and attestation permissions scoped to the jobs
that require them. Docker/dashboard jobs do not receive package-write permission unless a future
publishing workflow explicitly needs it.
