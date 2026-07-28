# Dependency management policy

Dependabot is the repository's sole automated dependency-update system. It owns
the Python, GitHub Actions, and Docker ecosystems defined in
`.github/dependabot.yml`; the machine-readable ownership contract is
`.github/dependency-policy.yaml`.

Dependabot pull requests are grouped by ecosystem, are never auto-merged, and
must pass the protected Python 3.14 path, lockfile checks, dependency audit,
immutable-action checks, and the repository contracts. Security scanning is an
independent required control, not a second update system.

Manual upgrades are permitted for urgent fixes or unavailable update metadata,
but must update `uv.lock` where applicable and retain the same verification
requirements. No additional Renovate, scheduled pip-upgrade, or ad hoc update
workflow is configured.
