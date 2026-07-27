<!-- GENERATED — DO NOT EDIT; run `make generate`. -->
# feat: Optional machine-readable OIA request and response receipts with no automatic submission.

## Problem

This reusable interface is currently implemented by a project-local oracle. It belongs upstream,
but the downstream open pipeline must continue to work before any upstream release.

## Proposed interface

Optional machine-readable OIA request and response receipts with no automatic submission.

Operations:

- `render_request`
- `receipt_manifest`
- `attachment_checksums`

Input contract: minimised request manifest, agency, status, licence notes, and supersession links.

Output contract: rendered hash plus request, response, and attachment receipt metadata.

## Compatibility fixture

- Deterministic Parquet fixture: `upstream/fixtures/fyi-cli.parquet`
- Local compatibility oracle: `src/closer_to_whom/integrations/fyi.py`
- Pinned repository identity: `8c0ddcd695ef60fff5f4feb6cb38074457386084` on `master`

## Acceptance

- `uv run pytest -q tests/unit/test_optional_integrations.py::test_fyi_render_is_optional_and_writes_output`
- Fixture round-trips with the canonical Arrow/Parquet schema and exact library identity.
- The upstream integration remains optional and the local oracle passes when it is unavailable.
- No project-specific policy semantics, person-level data, credentials, or licensed payloads enter the fixture.

## Handoff boundary

This is a patch-ready proposal, not evidence of an upstream issue, merge, release, suitability assessment,
security review, licence permission, endorsement, or execution of upstream code.
