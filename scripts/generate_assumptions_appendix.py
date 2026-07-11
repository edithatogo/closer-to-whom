#!/usr/bin/env python3
"""Generate a publication-ready assumptions appendix from canonical YAML."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assumptions" / "assumptions.yaml"
DEFAULT_OUT = ROOT / "docs" / "publication" / "assumptions-appendix.md"


def _items(payload: object) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        candidate = payload.get("assumptions", payload)
        if isinstance(candidate, list):
            return [item for item in candidate if isinstance(item, dict)]
        if isinstance(candidate, dict):
            items: list[dict[str, Any]] = []
            for key, value in candidate.items():
                if isinstance(value, dict):
                    row = dict(value)
                    row.setdefault("id", key)
                else:
                    row = {"id": key, "statement": value}
                items.append(row)
            return items
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    raise ValueError("Unsupported assumptions structure")


def _cell(item: dict[str, Any], key: str, fallback: str = "") -> str:
    value = item.get(key, fallback)
    if isinstance(value, list):
        value = "; ".join(map(str, value))
    if isinstance(value, dict):
        value = "; ".join(f"{k}: {v}" for k, v in sorted(value.items()))
    return str(value).replace("|", "\\|").replace("\n", " ")


def generate(output: Path) -> Path:
    payload = yaml.safe_load(SOURCE.read_text(encoding="utf-8"))
    rows = sorted(_items(payload), key=lambda item: str(item.get("id", "")))
    lines = [
        "# Appendix: explicit assumptions",
        "",
        "Generated from `assumptions/assumptions.yaml`; do not edit by hand.",
        "",
        "| ID | Assumption | Status | Uncertainty / sensitivity | Claim boundary |",
        "|---|---|---|---|---|",
    ]
    for item in rows:
        statement = (
            _cell(item, "statement") or _cell(item, "assumption") or _cell(item, "description")
        )
        if not statement:
            name = _cell(item, "name")
            value = _cell(item, "value")
            rationale = _cell(item, "rationale")
            statement = f"{name} = {value}. {rationale}".strip()
        uncertainty = _cell(item, "uncertainty") or _cell(item, "sensitivity")
        lines.append(
            f"| {_cell(item, 'id')} | {statement} | {_cell(item, 'status')} | "
            f"{uncertainty} | {_cell(item, 'claim_boundary')} |"
        )
    lines.extend(["", f"Total assumptions: **{len(rows)}**.", ""])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    print(generate(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
