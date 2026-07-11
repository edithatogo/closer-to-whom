#!/usr/bin/env python3
"""Validate conventional commit messages."""

from __future__ import annotations

import re
import sys
from pathlib import Path

PATTERN = re.compile(
    r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([^)]+\))?!?: .{3,}$"
)


def main() -> None:
    if len(sys.argv) < 2:
        return
    message = Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()[0]
    if message.startswith(("Merge ", "Revert ")):
        return
    if not PATTERN.match(message):
        raise SystemExit("Commit subject must follow Conventional Commits")


if __name__ == "__main__":
    main()
