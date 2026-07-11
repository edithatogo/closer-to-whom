#!/usr/bin/env python3
"""Fail when committed generated files differ from fresh generation."""

from __future__ import annotations

import filecmp
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(command: list[str], cwd: Path = ROOT) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def _compare_tree(expected: Path, generated: Path) -> list[str]:
    failures: list[str] = []
    if not expected.exists():
        return [f"missing committed generated directory: {expected.relative_to(ROOT)}"]
    comparison = filecmp.dircmp(expected, generated)

    def walk(node: filecmp.dircmp, prefix: Path) -> None:
        for name in node.left_only:
            failures.append(f"committed-only: {prefix / name}")
        for name in node.right_only:
            failures.append(f"generated-only: {prefix / name}")
        for name in node.diff_files:
            failures.append(f"different: {prefix / name}")
        for name in node.funny_files:
            failures.append(f"unreadable: {prefix / name}")
        for name, child in node.subdirs.items():
            walk(child, prefix / name)

    walk(comparison, Path(expected.name))
    return failures


def main() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="ctw-generated-") as raw:
        temp = Path(raw)
        json_out = temp / "json"
        arrow_out = temp / "arrow"
        assumptions_out = temp / "assumptions-appendix.md"

        _run(
            [
                sys.executable,
                "-c",
                (
                    "from pathlib import Path; "
                    "from scripts.generate_json_schemas import generate; "
                    f"generate(Path({str(json_out)!r}))"
                ),
            ]
        )
        _run([sys.executable, "scripts/generate_schema_registry.py", "--output", str(arrow_out)])
        _run(
            [
                sys.executable,
                "scripts/generate_assumptions_appendix.py",
                "--output",
                str(assumptions_out),
            ]
        )

        failures.extend(_compare_tree(ROOT / "schemas" / "json", json_out))
        failures.extend(_compare_tree(ROOT / "schemas" / "arrow", arrow_out))
        committed_appendix = ROOT / "docs" / "publication" / "assumptions-appendix.md"
        if not committed_appendix.exists():
            failures.append("missing committed assumptions appendix")
        elif committed_appendix.read_bytes() != assumptions_out.read_bytes():
            failures.append("different: docs/publication/assumptions-appendix.md")

    if failures:
        print("Generated-file drift detected:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        print(
            "Regenerate with `make generate` or `just generate` and commit the results.",
            file=sys.stderr,
        )
        return 1
    print("Generated files are current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
