# Incident response

Stop publication or dashboard deployment when a confidential datum, credential, unsupported clinical claim, source-licence conflict, schema-breaking change, reproducibility failure, or material model defect is identified.

1. Disable the affected artefact or deployment.
2. Preserve hashes, logs, revision, and source metadata without copying sensitive payloads into issues.
3. Classify severity and affected releases.
4. Rotate credentials or remove access where relevant.
5. Correct the source, model, or claim; add a regression test.
6. Re-run the full release gate and publish a transparent correction record.
7. For an already published scientific result, follow the journal and repository correction policy.
