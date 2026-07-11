# Reproducibility and clean-room verification

The release gate runs generation drift checks, schema and assumptions contracts, formatting, linting, type checks, property and metamorphic tests, differential acceleration tests, security scans, package build and isolated install, deterministic demonstration runs, documentation build, and release metadata checks. Optional capabilities are recorded as `skipped` rather than reported as passing when their toolchain is unavailable.

A result is publication-reproducible only when two clean runs from the same input and seed have identical canonical output digests, and when every input and assumption digest is present in the run manifest.
