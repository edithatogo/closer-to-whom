# Upstream contribution work

`upstream/contracts.yaml` is the canonical LIB-010 registry. It records each proposed interface,
reviewed public repository revision, generated Parquet compatibility fixture, local oracle, and concrete
acceptance command. Run `make generate` after changing it; generated issue bodies and fixtures must not
be edited directly, and CI fails on drift.

The downstream repository remains functional without unreleased upstream changes. The weekly upstream
watch validates all local contracts, compares live default-branch revisions with the reviewed pins, and
retains machine-readable compatibility and metadata artefacts. Revision drift fails closed and requires
an explicit contract review.

Prepared issue bodies are local patch-ready handoff material. They do not prove that an upstream issue
was opened, a patch was merged, a release is available, code was imported or executed, suitability was
assessed, licence permission was granted, or an upstream maintainer endorsed the proposal. Publishing
or modifying another repository requires a separately scoped action.

Once an upstream release exists, add a differential compatibility test against the pinned released
interface before deleting any local fallback.
