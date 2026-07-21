# Clinical review receipts

`data/public/clinical-pathway-review.yaml` separates software safety checks from external clinical
review. The committed state is `pending_external_review`, and synthetic pathway fixtures remain
non-evidence.

The receipt validator permits that explicit pending state. A reviewed state must list every required
review role, a dated receipt reference for each role, and at least one decision. It must also retain
the synthetic-fixture claim boundary. `make contracts` runs this check without converting a fixture
into clinical, funding, or eligibility guidance.
