"""Deterministic Arrow and Polars input/output helpers."""

from __future__ import annotations

from pathlib import Path

import polars as pl
import pyarrow as pa
import pyarrow.parquet as pq

from closer_to_whom.contracts import table_fingerprint


def write_parquet_deterministic(
    frame: pl.DataFrame,
    path: Path,
    *,
    sort_by: tuple[str, ...],
) -> str:
    """Write a sorted Parquet file and return a canonical Arrow content digest."""
    path.parent.mkdir(parents=True, exist_ok=True)
    sorted_frame = frame.sort(list(sort_by)) if sort_by else frame
    table = sorted_frame.to_arrow()
    pq.write_table(
        table,
        path,
        compression="zstd",
        compression_level=9,
        use_dictionary=False,
        write_statistics=True,
        data_page_version="2.0",
    )
    return table_fingerprint(table, sort_by=sort_by)


def read_parquet(path: Path) -> pl.DataFrame:
    """Read a Parquet dataset with Polars."""
    return pl.read_parquet(path)


def write_arrow_ipc(
    table: pa.Table,
    path: Path,
    *,
    sort_by: tuple[str, ...] = (),
) -> str:
    """Write deterministic Arrow IPC and return its canonical content digest."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if sort_by:
        table = table.sort_by([(column, "ascending") for column in sort_by])
    options = pa.ipc.IpcWriteOptions(compression=None)
    with (
        pa.OSFile(str(path), "wb") as sink,
        pa.ipc.new_file(sink, table.schema, options=options) as writer,
    ):
        writer.write_table(table.combine_chunks())
    return table_fingerprint(table, sort_by=sort_by)
