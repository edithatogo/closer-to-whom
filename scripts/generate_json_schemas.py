#!/usr/bin/env python3
"""Generate deterministic JSON Schemas for public model contracts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from closer_to_whom.models import (
    CostRates,
    DemandCell,
    Facility,
    Pathway,
    ResearchDesign,
    Scenario,
    SourceRecord,
    UncertaintyParameter,
    VisitType,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "schemas" / "json"
MODELS = (
    SourceRecord,
    Facility,
    DemandCell,
    VisitType,
    Pathway,
    Scenario,
    CostRates,
    UncertaintyParameter,
    ResearchDesign,
)


def _normalise(value: Any) -> Any:
    """Recursively sort mappings so generated schemas are byte-stable."""
    if isinstance(value, dict):
        return {key: _normalise(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [_normalise(item) for item in value]
    return value


def generate(output: Path = OUT) -> list[Path]:
    output.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for model in MODELS:
        payload = _normalise(model.model_json_schema(mode="validation"))
        path = output / f"{model.__name__}.schema.json"
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        written.append(path)
    index = {
        "schema_version": "1.0.0",
        "models": [
            {
                "model": model.__name__,
                "path": f"{model.__name__}.schema.json",
                "title": model.model_json_schema().get("title", model.__name__),
            }
            for model in MODELS
        ],
    }
    index_path = output / "index.json"
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    written.append(index_path)
    return written


if __name__ == "__main__":
    for generated in generate():
        print(generated.relative_to(ROOT))
