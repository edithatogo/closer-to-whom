# Public-data refresh

A refresh is a controlled model change, not a background scrape. The agent creates a Conductor track, resolves each source through the registry, records retrieval metadata and digest, applies licence gates, transforms through versioned Arrow schemas, compares semantic changes, and requests evidence review where service capability has changed.

No refresh may silently alter a frozen manuscript analysis. Publication datasets and results are content-addressed and immutable; a newer refresh creates a new analysis release.
