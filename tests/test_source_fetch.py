from __future__ import annotations

from pathlib import Path

import pytest

from closer_to_whom.source_fetch import FetchPolicy, SourceFetchError, fetch_public_source


def test_source_fetch_is_fail_closed(tmp_path: Path) -> None:
    with pytest.raises(SourceFetchError, match="disabled"):
        fetch_public_source(
            source_id="example",
            url="https://example.org/data.csv",
            destination=tmp_path / "data.csv",
            policy=FetchPolicy(),
        )


def test_source_fetch_requires_allowlisted_host(tmp_path: Path) -> None:
    with pytest.raises(SourceFetchError, match="allowlist"):
        fetch_public_source(
            source_id="example",
            url="https://example.org/data.csv",
            destination=tmp_path / "data.csv",
            policy=FetchPolicy(allow_network=True, allowed_hosts=("stats.govt.nz",)),
        )
