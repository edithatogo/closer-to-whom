"""Fetch an approved ADE area selection in bounded CSV chunks."""

from __future__ import annotations

import argparse
import csv
import io
import os
from pathlib import Path
from urllib.request import Request, urlopen


def _split_request(url: str) -> tuple[str, list[str], str]:
    path, query = url.split("?", 1)
    prefix, selection = path.rsplit(".", 1)
    codes = selection.split("+")
    if not codes or any(not code for code in codes):
        raise ValueError("request URL must contain a non-empty area selection")
    return prefix, codes, query


def fetch(url: str, output: Path, chunk_size: int = 100) -> int:
    token = os.environ.get("STATS_NZ_API_KEY")
    if not token:
        raise RuntimeError("STATS_NZ_API_KEY is required")
    prefix, codes, query = _split_request(url)
    if chunk_size < 1:
        raise ValueError("chunk_size must be positive")
    header: list[str] | None = None
    rows: list[list[str]] = []
    for start in range(0, len(codes), chunk_size):
        chunk_url = f"{prefix}.{'+'.join(codes[start : start + chunk_size])}?{query}"
        request = Request(
            chunk_url, headers={"Accept": "text/csv", "Ocp-Apim-Subscription-Key": token}
        )
        with urlopen(request, timeout=120) as response:
            content_type = response.headers.get("Content-Type", "")
            if "csv" not in content_type.lower():
                raise RuntimeError(f"chunk returned non-CSV content type: {content_type}")
            parsed = list(csv.reader(io.StringIO(response.read().decode("utf-8-sig"))))
        if not parsed:
            raise RuntimeError("chunk returned an empty CSV")
        if header is None:
            header = parsed[0]
        elif parsed[0] != header:
            raise RuntimeError("chunk CSV headers differ")
        rows.extend(parsed[1:])
    assert header is not None
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("request_url", type=str)
    parser.add_argument("output_csv", type=Path)
    parser.add_argument("--chunk-size", type=int, default=100)
    args = parser.parse_args()
    print(fetch(args.request_url, args.output_csv, args.chunk_size))


if __name__ == "__main__":
    main()
