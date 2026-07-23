"""Materialise an approved Stats NZ CSV response as aggregate Parquet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import polars as pl

FORBIDDEN = {"patient", "patient_id", "nhs_number", "name", "address", "phone", "email"}


def materialize(source: Path, output: Path, report: Path) -> None:
    frame = pl.read_csv(source)
    if frame.is_empty():
        raise ValueError("Stats NZ CSV is empty")
    columns = {column.casefold().replace(" ", "_") for column in frame.columns}
    forbidden = sorted(columns & FORBIDDEN)
    if forbidden:
        raise ValueError(f"CSV contains forbidden individual-level columns: {forbidden}")
    if len(frame.columns) != len(set(frame.columns)):
        raise ValueError("CSV contains duplicate column names")
    output.parent.mkdir(parents=True, exist_ok=True)
    frame.write_parquet(output, compression="zstd")
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "rows": frame.height,
                "columns": frame.columns,
                "claim_boundary": "Aggregate population denominator only; never patient records.",
                "source_format": "text/csv",
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    materialize(args.source, args.output, args.report)


if __name__ == "__main__":
    main()
