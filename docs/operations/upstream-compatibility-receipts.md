# Upstream compatibility receipts

Optional upstream libraries and CLIs are integration candidates, not mandatory runtime
dependencies. The compatibility contract checks that each discovered capability has a mechanism and
role, that no optional tool is required for the open pipeline, and that the repository retains its
upstream issue and local fallback boundary.

An unavailable capability is reported as unavailable; it is never treated as evidence that the
underlying service or data is absent. Promotion to a production dependency requires a separately
reviewed compatibility receipt and a pinned upstream release.
