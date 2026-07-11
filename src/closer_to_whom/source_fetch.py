"""Fail-closed retrieval and snapshotting of explicitly registered public sources."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Final

MAX_DEFAULT_BYTES: Final = 250 * 1024 * 1024


class SourceFetchError(RuntimeError):
    """Raised when a public source cannot be retrieved under the declared policy."""


@dataclass(frozen=True, slots=True)
class FetchPolicy:
    """Security and reproducibility limits for a source retrieval."""

    allow_network: bool = False
    allowed_hosts: tuple[str, ...] = ()
    max_bytes: int = MAX_DEFAULT_BYTES
    timeout_seconds: int = 60
    user_agent: str = "closer-to-whom-public-data-research/0.2"


@dataclass(frozen=True, slots=True)
class FetchReceipt:
    """Machine-readable receipt for immutable source bytes."""

    source_id: str
    url: str
    retrieved_unix_seconds: int
    sha256: str
    bytes: int
    content_type: str
    etag: str | None
    last_modified: str | None
    output_path: str

    def as_json(self) -> str:
        return json.dumps(asdict(self), indent=2, sort_keys=True) + "\n"


def _host_allowed(url: str, hosts: tuple[str, ...]) -> bool:
    from urllib.parse import urlsplit

    hostname = (urlsplit(url).hostname or "").lower()
    return any(hostname == allowed.lower() or hostname.endswith(f".{allowed.lower()}") for allowed in hosts)


def _stream_to_temp(response: object, destination: Path, max_bytes: int) -> tuple[int, str]:
    digest = hashlib.sha256()
    total = 0
    with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as handle:
        temp_path = Path(handle.name)
        while True:
            chunk = response.read(1024 * 1024)  # type: ignore[attr-defined]
            if not chunk:
                break
            total += len(chunk)
            if total > max_bytes:
                handle.close()
                temp_path.unlink(missing_ok=True)
                raise SourceFetchError(f"source exceeds declared maximum of {max_bytes} bytes")
            digest.update(chunk)
            handle.write(chunk)
    os.replace(temp_path, destination)
    return total, digest.hexdigest()


def fetch_public_source(
    *,
    source_id: str,
    url: str,
    destination: Path,
    policy: FetchPolicy,
) -> FetchReceipt:
    """Retrieve a registered public source only when network and host are explicit."""

    if not policy.allow_network:
        raise SourceFetchError("network retrieval is disabled; pass an explicit reviewed policy")
    if not _host_allowed(url, policy.allowed_hosts):
        raise SourceFetchError("source host is not present in the reviewed allowlist")
    if not url.startswith("https://"):
        raise SourceFetchError("only HTTPS public sources are permitted")

    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": policy.user_agent,
            "Accept-Encoding": "identity",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=policy.timeout_seconds) as response:  # noqa: S310
            status = getattr(response, "status", 200)
            if status != 200:
                raise SourceFetchError(f"unexpected HTTP status {status}")
            total, digest = _stream_to_temp(response, destination, policy.max_bytes)
            headers = response.headers
            receipt = FetchReceipt(
                source_id=source_id,
                url=url,
                retrieved_unix_seconds=int(time.time()),
                sha256=digest,
                bytes=total,
                content_type=str(headers.get("Content-Type", "application/octet-stream")),
                etag=headers.get("ETag"),
                last_modified=headers.get("Last-Modified"),
                output_path=str(destination),
            )
    except urllib.error.URLError as exc:
        raise SourceFetchError(f"source retrieval failed: {exc}") from exc

    receipt_path = destination.with_suffix(destination.suffix + ".receipt.json")
    receipt_path.write_text(receipt.as_json(), encoding="utf-8")
    return receipt
