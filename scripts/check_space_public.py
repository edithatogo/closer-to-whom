#!/usr/bin/env python3
"""Probe the public Static Space and emit a non-secret availability receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

MARKERS = ("Closer to whom", "Research boundary", "aggregate")


def probe(url: str, timeout: int = 20) -> dict[str, object]:
    request = Request(url, headers={"User-Agent": "closer-to-whom-space-monitor/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:  # noqa: S310
            body = response.read()
            status = int(response.status)
            content_type = response.headers.get("Content-Type", "")
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"Public Space probe failed: {exc}") from exc
    text = body.decode("utf-8", errors="replace")
    missing = [marker for marker in MARKERS if marker.lower() not in text.lower()]
    if status != 200 or missing:
        raise RuntimeError(f"Public Space contract failed: status={status}, missing={missing}")
    return {
        "schema_version": "1.0.0",
        "url": url,
        "status": "passed",
        "http_status": status,
        "content_type": content_type,
        "body_sha256": hashlib.sha256(body).hexdigest(),
        "markers": list(MARKERS),
        "checked_at": datetime.now(UTC).isoformat(),
        "claim_boundary": "Availability and public-content smoke check only; not deployment, clinical, or policy validation.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--output", type=Path, default=Path("release/space-monitor-receipt.json"))
    args = parser.parse_args()
    receipt = probe(args.url)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
