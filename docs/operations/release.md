# Release runbook

1. Freeze source, service census, pathway, assumptions, and scenario versions.
2. Confirm no unresolved Grade 1/2 service disagreements.
3. Refresh time-sensitive cost, funding, regulatory, and publication requirements.
4. Run the clean locked environment and all test matrices.
5. Run the model twice and compare canonical Arrow content digests.
6. Build package, docs, dashboard image, SBOM, and provenance manifest.
7. Scan image and repository for prohibited data and secrets.
8. Generate assumptions appendix, result dictionary, model card, and manuscript tables.
9. Review clinical, equity, cultural, statistical, economic, and policy interpretations.
10. Sign and tag the release; archive code, permitted data manifests, and DOI artefacts.
11. Deploy the exact digest-tested dashboard image.
12. Monitor source changes and disclose superseded releases.

`make release-gate` automates every locally executable step and records unavailable external gates for handover.
