# Option A release plan

Option A is the signed public release path. It is preparation only until the owner confirms the
signing identity, archive destination, and publication action.

## Current recommendation

Use an owner-controlled SSH signing key for the Git tag, because an SSH private key is present in the
local release environment while no GPG signing key is configured. Use Zenodo as the independent
archive target, creating a new project record only after the owner confirms that destination. GitHub
Release is the secondary mirror.

This recommendation is not an authorization to use a key, create a tag, upload files, or publish.

## Execution sequence

1. Confirm the exact SSH public key fingerprint and the owner’s authorization to use it for release signing.
2. Run the complete release gate from a clean `main` checkout and record its exact revision.
3. Generate the release manifest, SBOM, attestations, source bundle, distributions, and checksums.
4. Create and verify the signed `v0.2.0-rc.1` tag; stop if verification fails.
5. Upload only the permitted derived release bundle and receipts to the owner-approved Zenodo record.
6. Verify archive checksums and recovery of source, package, reports, SBOM, and Space receipts.
7. Publish the GitHub Release as a mirror only after independent archive recovery passes.

## Contingencies

- If the SSH key is unavailable, mismatched, or cannot be verified, retain Option C and do not create
  an unsigned tag.
- If Zenodo destination or upload authorization is unavailable, retain the hosted candidate and do
  not claim independent durability.
- If any archive checksum or recovery hash differs, keep the release unpublished and record the
  mismatch against CTW-100d.
- If the Space revision differs from the approved release revision, republish and rerun assurance
  before any archive or GitHub Release action.

## Owner decisions still required

- Confirm the SSH key fingerprint or provide another signing mechanism.
- Confirm the Zenodo project/record and whether publication should be public.
- Authorize the action-time tag, upload, recovery verification, and GitHub Release mirror.
