# Clinical review receipts

`data/public/clinical-pathway-review.yaml` separates software safety checks from clinical
attestation. The committed sole-developer receipt is `reviewed`; the reviewer is recorded as a
qualified clinician and no second GitHub reviewer is required. Synthetic pathway fixtures still
remain non-evidence.

The reviewed state lists every required scope, a dated receipt reference for each scope, and the
accepted decisions. Product and funding constraints are recorded separately in
`data/public/clinical-pathway-evidence.yaml`; home, community, and hybrid pathways remain unfrozen
counterfactuals. `make contracts` validates these boundaries without converting a fixture into
clinical guidance or facility evidence.
