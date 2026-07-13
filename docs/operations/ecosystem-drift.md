# Ecosystem metadata drift

The scheduled `ecosystem-drift` workflow queries only public GitHub repository
metadata and emits a non-blocking JSON report. It compares default branch,
archived/fork state, SPDX identifier, and update timestamp with the frozen
catalogue.

The report never rewrites the catalogue, changes suitability decisions, clones
repositories, or imports/builds/executes external code. Rate limits and deleted
or inaccessible public repositories are recorded as `unavailable`; they are not
treated as unchanged.
