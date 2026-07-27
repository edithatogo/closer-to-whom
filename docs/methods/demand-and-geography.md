# Aggregate demand and geography

Expected treatment courses are estimated at a public geography and stratum level:

\[
D_{agr}=N_{ag}I_{agr}P(\mathrm{HER2+})P(\mathrm{eligible}\mid r)P(\mathrm{treated}\mid r).
\]

The model calibrates to public national or regional totals where available. It does not claim that small-area demand is observed.

SA2 under Stats NZ's Statistical Standard for Geographic Areas 2023 (SSGA23) is the principal geography. The baseline uses each official SA2 true centroid; a separate sensitivity uses positive-population SA1 centroids with weights that reconcile to one within every SA2. Public outputs aggregate back to SA2. The public-input manifest is frozen for authorised local use with source-level provenance and redistribution boundaries retained.

The ADE workflow accepts only an exact, interface-generated data query; wildcard area syntax is rejected. Each approved structure response is accompanied by an offline codelist inventory from `scripts/inspect_stats_nz_structure.py`. The materialized denominator uses the corrected 2,314-code request, bounded requests, validated CSV responses, and deterministic concatenation; 2,313 positive denominator rows enter the model.

Ethnicity uses six overlapping total-response broad groups and is never treated as an exclusive individual attribute. Stats NZ Urban Rural 2023 is the open baseline rurality stratifier, separate from network travel. NZDep2023 and household no-motor-vehicle prevalence remain ecological context; suppressed or unmatched values remain explicit unknowns. GCH23 remains an unredistributed optional sensitivity because of its CC BY-ND terms.
