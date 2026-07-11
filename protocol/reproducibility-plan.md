# Reproducibility plan

A publication candidate must be rebuildable from a clean clone using a locked dependency graph and a documented toolchain. Generation, simulation, and summary steps must be deterministic for a recorded seed and input manifest. A clean-room receipt records source revision, dirty state, platform, Python version, dependency lock digest, assumptions digest, schema fingerprints, input digests, command outcomes, and output digests.

The public release will archive the Git revision, source bundle, machine-readable manifest, SBOM, assumptions appendix, schema registry, synthetic demonstration output, and validation receipt. Restricted or non-redistributable inputs will be represented only by retrieval instructions, source metadata, and checksums where permitted.
