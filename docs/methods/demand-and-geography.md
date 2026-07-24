# Aggregate demand and geography

Expected treatment courses are estimated at a public geography and stratum level:

\[
D_{agr}=N_{ag}I_{agr}P(\mathrm{HER2+})P(\mathrm{eligible}\mid r)P(\mathrm{treated}\mid r).
\]

The model calibrates to public national or regional totals where available. It does not claim that small-area demand is observed.

SA2 under Stats NZ's Statistical Standard for Geographic Areas 2023 (SSGA23) is the planned principal geography. Each area is represented by several public population-weighted routing points rather than one geometric centroid. Allocation weights sum to one and are resampled in spatial uncertainty analysis. Public outputs aggregate back to an appropriate geography. The SSGA23 input and licence freeze remains pending.

The ADE workflow accepts only an exact, interface-generated data query; wildcard area syntax is rejected. Each approved structure response is therefore accompanied by an offline codelist inventory from `scripts/inspect_stats_nz_structure.py`. The inventory supports review of the SA2 codelist without guessing codes or constructing an unapproved query; the exact SA2 request remains an explicit input-freeze gate.

Ethnicity uses an explicitly documented representation, with total-response and prioritised approaches treated as separate analyses where available. GCH23 is the planned rurality stratifier, separate from network travel and subject to its restricted CC BY-ND redistribution terms. Deprivation, vehicle access, disability, and mobility measures remain contextual area-level variables.
