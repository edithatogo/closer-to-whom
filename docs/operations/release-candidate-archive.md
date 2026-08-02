# Release-candidate signing and archive handoff

This runbook is intentionally fail-closed. This is a single-person repository: the owner is the
sole human authority for release, signing, archive, publication, and governance decisions. Agents
may provide panel advice with options, rationale, risks, contingencies, and a recommendation, but
agent output is not approval. The runbook does not create a signature, publish a release, or claim
independent durability without the owner's action-time decision, credentials, and destination.

## Preconditions

- `main` is clean and the release gate passes.
- The release candidate revision is recorded in `conductor/state.yaml` and the release receipts.
- The candidate version and support status have been approved.
- A signing key is available in the release environment.
- An OSF or Zenodo project and authenticated upload method have been selected.

## Prepare the candidate

From a clean checkout of `main`:

```powershell
make release-gate
uv run python scripts/create_release_manifest.py
uv run python scripts/generate_sbom.py --output release/sbom.cdx.json
```

Review the manifest, SBOM, attestations, Space receipt, recovery receipt, and claim boundary before
any tag or upload action.

## Sign and tag

Use the approved signing key and an explicit release-candidate tag, for example:

```powershell
git tag -s v0.2.0-rc.1 -m "Closer to whom? v0.2.0 release candidate" <approved-revision>
git tag -v v0.2.0-rc.1
git push origin v0.2.0-rc.1
```

Do not substitute an unsigned tag. If signing verification fails, stop and retain the candidate as
untagged repository evidence.

## Archive

Upload only the permitted derived bundle and its machine-readable receipts to the approved OSF or
Zenodo project. Do not upload restricted raw inputs, live Healthpoint payloads, credentials, or private
data. Record the archive DOI/project, item/version identifier, upload timestamp, archive checksum, and
the exact source revision in a receipt.

Keep the GitHub Release as a public secondary mirror, with the same manifest and checksums.

## Recovery verification

Download the independent archive into a clean temporary directory and verify:

```powershell
Get-FileHash .\* -Algorithm SHA256
uv run python scripts/recovery_drill.py
```

The archive gate closes only when source, package, report, SBOM, and deployed Space hashes match the
approved receipt. Otherwise record the mismatch and keep CTW-100d open.
