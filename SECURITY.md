# Security policy

## Reporting a vulnerability

Report security, privacy, data-licence, or provenance concerns privately through
[GitHub Security Advisories](https://github.com/edithatogo/closer-to-whom/security/advisories/new).
Do not include confidential payloads, health-service data, credentials, or live Healthpoint
responses in a public issue or pull request.

Please include the affected revision, a minimal reproducible description, and the impact. We aim to
acknowledge a report within 7 days, provide an initial assessment within 14 days, and coordinate a
fix or public disclosure timeline with the reporter. Do not test against production services or
attempt to access data outside the public aggregate scope.

Supported releases are the latest tagged release and `main`. The project intentionally fails closed
on live Healthpoint data, unknown redistribution rights, secrets, and prohibited data paths.

## Verified repository security controls

As of 2026-07-21, the public repository reports secret scanning, push protection,
and Dependabot security updates as enabled. GitHub reports non-provider secret-pattern
scanning and secret validity checks as disabled/unavailable at the current account or
plan capability; this repository does not represent those controls as enabled.

The repository owner (`edithatogo`) is the enablement owner. The exact request is:
"Enable secret-scanning non-provider patterns and secret validity checks for
edithatogo/closer-to-whom, or enable the GitHub account/organisation plan capability
that makes those repository controls available." Until GitHub confirms that change,
the local secret scan, push protection, least-privilege workflows, and dependency
checks remain the enforceable controls.
