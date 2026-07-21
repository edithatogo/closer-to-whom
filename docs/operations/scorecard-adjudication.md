# Scorecard alert adjudication

The repository ruleset retains active CodeQL and Scorecard scanning. Historical Scorecard alerts
from the pre-hardening `main` baseline were individually reviewed on 2026-07-21 and dismissed with
comments in GitHub because they were either superseded by the protected implementation branch or
were documented governance exceptions:

- workflow and container dependency findings are superseded by full-length action pins, digest-pinned
  Python images, and hash-locked `uv 0.11.29` bootstrap requirements;
- the security-policy finding is superseded by the private GitHub Security Advisory process in
  `SECURITY.md`;
- the fuzzing finding is superseded by the pinned Python 3.14 Hypothesis fuzz workflow;
- maintenance and OpenSSF Best Practices findings are age/registration observations, not code
  defects; and
- branch-protection and code-review findings document the intentional single-maintainer policy:
  deletion and force-push are prohibited, required CI/security checks and review-thread resolution
  remain active, and no bypass actors are configured.

Future default-branch Scorecard scans remain authoritative. A newly detected alert must be fixed or
individually adjudicated; this record is not a blanket suppression rule.
