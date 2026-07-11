#!/usr/bin/env python3
"""Fail closed when the committed uv lock leaks private indexes or is not portable."""

from __future__ import annotations

import re
import tomllib
from collections.abc import Iterator, Mapping, Sequence
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = ROOT / "uv.lock"
PROJECT_PATH = ROOT / "pyproject.toml"

FORBIDDEN_TOKENS = (
    "applied-caas",
    "internal.api.openai.org",
    "artifactory/api/pypi",
    "reader:",
)
ALLOWED_REGISTRY_HOSTS = {"pypi.org"}
ALLOWED_ARTIFACT_HOSTS = {"files.pythonhosted.org"}
CREDENTIAL_URL = re.compile(r"https?://[^/\s:@]+:[^/\s@]+@", re.IGNORECASE)


def _normalise_specifier(value: str) -> str:
    return "".join(value.split())


def _walk_urls(value: Any) -> Iterator[str]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key in {"url", "registry"} and isinstance(child, str):
                yield child
            yield from _walk_urls(child)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for child in value:
            yield from _walk_urls(child)


def main() -> None:
    if not LOCK_PATH.exists():
        raise SystemExit("uv.lock is required for a handover release")

    text = LOCK_PATH.read_text(encoding="utf-8")
    lowered = text.lower()
    failures: list[str] = []

    for token in FORBIDDEN_TOKENS:
        if token.lower() in lowered:
            failures.append(f"uv.lock contains forbidden private-index token: {token}")
    if CREDENTIAL_URL.search(text):
        failures.append("uv.lock contains a credential-bearing URL")
    if "files.pythonhosted.org/packages/packages/" in text:
        failures.append("uv.lock contains a malformed double /packages/ artifact path")

    lock = tomllib.loads(text)
    project = tomllib.loads(PROJECT_PATH.read_text(encoding="utf-8"))
    lock_requires = str(lock.get("requires-python", ""))
    project_requires = str(project["project"].get("requires-python", ""))
    if _normalise_specifier(lock_requires) != _normalise_specifier(project_requires):
        failures.append(
            "uv.lock requires-python differs from pyproject.toml: "
            f"{lock_requires!r} != {project_requires!r}"
        )

    packages = lock.get("package", [])
    if not isinstance(packages, list) or not packages:
        failures.append("uv.lock has no package records")
    for url in _walk_urls(packages):
        parsed = urlparse(url)
        if parsed.scheme not in {"https", "file"}:
            failures.append(f"unsupported lock URL scheme: {url}")
            continue
        if parsed.scheme == "file":
            continue
        host = (parsed.hostname or "").lower()
        if url.rstrip("/").endswith("/simple"):
            if host not in ALLOWED_REGISTRY_HOSTS:
                failures.append(f"non-public registry host in uv.lock: {host or url}")
        elif host not in ALLOWED_ARTIFACT_HOSTS:
            failures.append(f"non-public artifact host in uv.lock: {host or url}")

    if failures:
        raise SystemExit("\n".join(sorted(set(failures))))
    print(
        "Portable uv.lock passed: "
        f"{len(packages)} package records, public PyPI endpoints only, no embedded credentials."
    )


if __name__ == "__main__":
    main()
