#!/usr/bin/env python3
"""Dependency-free AST complexity and function-size budget."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "closer_to_whom"
MAX_STATEMENTS = 80
MAX_BRANCHES = 20

BRANCH_NODES = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.Match, ast.BoolOp, ast.IfExp)


def statement_count(node: ast.AST) -> int:
    return sum(isinstance(child, ast.stmt) for child in ast.walk(node))


def branch_count(node: ast.AST) -> int:
    return sum(isinstance(child, BRANCH_NODES) for child in ast.walk(node))


def main() -> int:
    failures = []
    for path in sorted(SOURCE.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                statements = statement_count(node)
                branches = branch_count(node)
                if statements > MAX_STATEMENTS or branches > MAX_BRANCHES:
                    failures.append(
                        f"{path.relative_to(ROOT)}:{node.lineno} {node.name}: "
                        f"statements={statements}/{MAX_STATEMENTS}, branches={branches}/{MAX_BRANCHES}"
                    )
    if failures:
        print("Complexity budget exceeded:", file=sys.stderr)
        print("\n".join(f"- {item}" for item in failures), file=sys.stderr)
        return 1
    print("Complexity budget passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
