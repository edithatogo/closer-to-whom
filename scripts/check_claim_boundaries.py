#!/usr/bin/env python3
"""Detect publication language that exceeds the open model's claim boundary."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAN_ROOTS = (ROOT / "docs", ROOT / "manuscript", ROOT / "src/closer_to_whom/dashboard")
EXCLUDED = {ROOT / "docs/operations/testing.md"}
PATTERNS = {
    r"\bproved that decentralis": "Causal proof language is prohibited",
    r"\bactual patient journeys? (?:were|are)": "Actual journeys are not observed",
    r"\bcurrent capacity (?:is|was)": "Current capacity is not observed",
    r"\bpatients? prefer(?:red|s)?\b": "Preferences are not observed in the open phase",
    r"\bcaused (?:better|worse|improved|reduced)": "Causal effects are not estimated",
}


def main() -> None:
    failures: list[str] = []
    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in {".md", ".py", ".qmd"} or path in EXCLUDED:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for pattern, message in PATTERNS.items():
                for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                    line = text.count("\n", 0, match.start()) + 1
                    failures.append(f"{path.relative_to(ROOT)}:{line}: {message}: {match.group(0)!r}")
    if failures:
        raise SystemExit("\n".join(failures))
    print("Claim-boundary scan passed.")


if __name__ == "__main__":
    main()
