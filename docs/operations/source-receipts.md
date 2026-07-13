# Source retrieval receipts

Source capture is a two-stage operation. The registry first records a candidate source and its
licence boundary. A source becomes `captured`, `adjudicated`, `active`, or `frozen` only when it
also declares an in-repository receipt path and evidence grade.

Use the explicit host allowlist when retrieving a registered public source:

```bash
uv run python scripts/fetch_public_source.py candidate.example --allow-network \
  --output /absolute/path/outside-the-repository/source.bin
```

The fetcher writes a SHA-256 receipt beside the retrieved bytes. Copy only the receipt into the
declared repository-controlled receipt location after licence review; raw, licensed, or restricted
payloads remain outside the repository. `make contracts` validates receipt identity, URL, hash,
retrieval timestamp, content type, and the captured-source evidence grade.

Pending candidates are intentionally allowed to have no receipt. This preserves the distinction
between a source candidate and an evidence-backed service claim. Healthpoint payloads additionally
require explicit licence evidence before `redistribution_allowed` can be true.
