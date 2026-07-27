"""Materialise NZDep2023 SA2 values with explicit unknowns for unmatched areas."""

from __future__ import annotations

import argparse
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import polars as pl

from closer_to_whom.io import write_parquet_deterministic

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / ".tmp/NZDep2023_WgtAvSA2.xlsx"
DEFAULT_POPULATION = ROOT / "data/derived/stats-nz-population.parquet"
DEFAULT_OUTPUT = ROOT / "data/derived/sa2-deprivation.parquet"
DEFAULT_REPORT = ROOT / "reports/sa2-deprivation.json"
SOURCE_ID = "candidate.nzdep2023"
SOURCE_SHA256 = "9a7392a72f6412399ce44fc4d7ae84fd816514f31e4eb03327d298407d1b0f2a"
MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
CELL_COLUMN = re.compile(r"[A-Z]+")


def _shared_strings(archive: ZipFile) -> list[str]:
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    return [
        "".join(node.text or "" for node in item.iter(f"{{{MAIN_NS}}}t"))
        for item in root
    ]


def _cell_value(cell: ET.Element, shared: list[str]) -> str | None:
    value = cell.find(f"{{{MAIN_NS}}}v")
    if value is None or value.text is None:
        return None
    if cell.attrib.get("t") == "s":
        return shared[int(value.text)]
    return value.text


def read_nzdep_xlsx(path: Path) -> pl.DataFrame:
    """Read the fixed public workbook without adding a runtime Excel dependency."""
    with ZipFile(path) as archive:
        shared = _shared_strings(archive)
        root = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
    rows: list[dict[str, object]] = []
    sheet_rows = root.findall(f".//{{{MAIN_NS}}}sheetData/{{{MAIN_NS}}}row")
    for row in sheet_rows[1:]:
        cells: dict[str, str | None] = {}
        for cell in row.findall(f"{{{MAIN_NS}}}c"):
            reference = cell.attrib.get("r", "")
            match = CELL_COLUMN.match(reference)
            if match:
                cells[match.group()] = _cell_value(cell, shared)
        code = cells.get("A")
        if not code:
            continue
        decile = cells.get("C")
        score = cells.get("D")
        rows.append(
            {
                "geography_code": str(code),
                "geography_name_nzdep2023": cells.get("B"),
                "deprivation_decile": int(decile) if decile else None,
                "deprivation_score": int(score) if score else None,
                "sa3_code_2023": cells.get("E"),
                "sa3_name_2023": cells.get("F"),
            }
        )
    return pl.DataFrame(
        rows,
        schema={
            "geography_code": pl.String,
            "geography_name_nzdep2023": pl.String,
            "deprivation_decile": pl.Int8,
            "deprivation_score": pl.Int32,
            "sa3_code_2023": pl.String,
            "sa3_name_2023": pl.String,
        },
    )


def materialize(
    source_path: Path,
    population_path: Path,
    output_path: Path,
    report_path: Path,
) -> dict[str, object]:
    source = read_nzdep_xlsx(source_path)
    population = (
        pl.read_parquet(population_path)
        .select(
            pl.col("AREA_POPES_SUB_004").cast(pl.String).alias("geography_code"),
            pl.col("OBS_VALUE").cast(pl.Int64).alias("population_2025"),
        )
        .unique(subset="geography_code")
    )
    joined = (
        population.join(source, on="geography_code", how="left")
        .with_columns(
            pl.when(pl.col("deprivation_decile").is_not_null())
            .then(pl.lit("matched_nzdep2023_sa2_code"))
            .when(pl.col("geography_name_nzdep2023").is_not_null())
            .then(pl.lit("unknown_source_value_blank"))
            .otherwise(pl.lit("unknown_sa2_version_mismatch"))
            .alias("deprivation_status")
        )
        .sort("geography_code")
    )
    matched = joined.filter(pl.col("deprivation_decile").is_not_null()).height
    blank = joined.filter(pl.col("deprivation_status") == "unknown_source_value_blank").height
    mismatch = joined.filter(
        pl.col("deprivation_status") == "unknown_sa2_version_mismatch"
    ).height
    if matched + blank + mismatch != population.height:
        raise ValueError("NZDep classification counts do not reconcile")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fingerprint = write_parquet_deterministic(
        joined, output_path, sort_by=("geography_code",)
    )
    report: dict[str, object] = {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(UTC).isoformat(),
        "status": "materialized_with_explicit_unknowns",
        "source_id": SOURCE_ID,
        "source_sha256": SOURCE_SHA256,
        "population_reference_year": 2025,
        "source_geography_version": "SA2 2023",
        "rows": population.height,
        "matched_rows": matched,
        "unknown_source_value_blank_rows": blank,
        "unknown_sa2_version_mismatch_rows": mismatch,
        "parquet_fingerprint": fingerprint,
        "claim_boundary": (
            "NZDep is an ecological area measure, never an individual attribute. "
            "Unmatched or source-blank areas remain unknown."
        ),
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--population", type=Path, default=DEFAULT_POPULATION)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    print(
        json.dumps(
            materialize(args.source, args.population, args.output, args.report),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
