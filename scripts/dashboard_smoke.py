#!/usr/bin/env python3
"""Smoke-test the aggregate dashboard application factory."""

from __future__ import annotations

import tempfile
from pathlib import Path

from closer_to_whom.pipeline import run_demo


def main() -> None:
    try:
        from closer_to_whom.dashboard.app import create_app
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory)
        run_demo(output)
        app = create_app(output)
        client = app.server.test_client()
        response = client.get("/")
        if response.status_code != 200:
            raise SystemExit(f"Dashboard returned HTTP {response.status_code}")
    print("Dashboard smoke test passed.")


if __name__ == "__main__":
    main()
