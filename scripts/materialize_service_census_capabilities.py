"""Materialise explicit capability states for the public service census."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data/public/service-census-records.yaml"
OUTPUT = ROOT / "data/public/service-census-capabilities.yaml"

CLAIMS = (
    "facility_existence",
    "oncology_presence",
    "solid_tumour_sact",
    "iv_trastuzumab",
    "trastuzumab_sc",
    "phesgo_sc",
    "outreach",
    "consultation_only",
)


def materialize(input_path: Path = INPUT, output_path: Path = OUTPUT) -> dict[str, Any]:
    payload = yaml.safe_load(input_path.read_text(encoding="utf-8")) or {}
    records = payload.get("records", [])
    if not isinstance(records, list):
        raise TypeError("service census records must be a list")
    output_records: list[dict[str, Any]] = []
    for record in records:
        if not isinstance(record, dict):
            raise TypeError("each service census record must be a mapping")
        source_ids = list(record.get("source_ids", []))
        claims = {
            "facility_existence": "confirmed",
            "oncology_presence": "confirmed",
            "solid_tumour_sact": "unknown",
            "iv_trastuzumab": "unknown",
            "trastuzumab_sc": "unknown",
            "phesgo_sc": "unknown",
            "outreach": "unknown",
            "consultation_only": "unknown",
        }
        output_records.append(
            {
                "facility_id": record["facility_id"],
                "source_ids": source_ids,
                "review_state": "pending_external_review",
                "temporal_status": "current_documented_source",
                "public_or_private": record["public_or_private"],
                "claims": claims,
            }
        )
    result = {
        "schema_version": "1.0.0",
        "generated_from": input_path.relative_to(ROOT).as_posix(),
        "claim_keys": list(CLAIMS),
        "records": output_records,
        "claim_boundary": (
            "Capability states are separate from facility existence. Unknown is not absent; "
            "no drug-specific anti-HER2 capability is inferred from generic oncology evidence."
        ),
    }
    output_path.write_text(
        yaml.safe_dump(result, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
        newline="\n",
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=INPUT)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    result = materialize(args.input, args.output)
    print(f"Materialised {len(result['records'])} capability records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
