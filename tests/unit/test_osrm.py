from urllib.parse import parse_qs, urlparse

import polars as pl
import pytest

from closer_to_whom.osrm import LocalOsrmTableClient


def test_osrm_is_loopback_only() -> None:
    with pytest.raises(ValueError, match="loopback"):
        LocalOsrmTableClient("https://router.project-osrm.org", "6.0.0")


def test_osrm_table_batches_and_records_engine() -> None:
    requested: list[str] = []

    def fetcher(url: str) -> dict:
        requested.append(url)
        query = parse_qs(urlparse(url).query)
        source_count = len(query["sources"][0].split(";"))
        destination_count = len(query["destinations"][0].split(";"))
        return {
            "code": "Ok",
            "distances": [[1000.0] * destination_count for _ in range(source_count)],
            "durations": [[120.0] * destination_count for _ in range(source_count)],
        }

    origins = pl.DataFrame(
        {
            "demand_cell_id": ["b", "a", "c"],
            "latitude": [-41.0, -40.0, -42.0],
            "longitude": [174.0, 175.0, 173.0],
        }
    )
    destinations = pl.DataFrame(
        {
            "facility_id": ["f1"],
            "latitude": [-41.1],
            "longitude": [174.1],
        }
    )
    result = LocalOsrmTableClient(
        "http://127.0.0.1:5000", "6.0.0", fetcher=fetcher, origin_batch_size=2
    ).matrix(origins, destinations)
    assert len(requested) == 2
    assert result["demand_cell_id"].to_list() == ["a", "b", "c"]
    assert result["one_way_km"].to_list() == [1.0, 1.0, 1.0]
    assert result["one_way_minutes"].to_list() == [2.0, 2.0, 2.0]
    assert result["route_engine"].unique().to_list() == ["osrm"]
    assert result["route_is_approximation"].unique().to_list() == [False]


def test_osrm_fails_closed_on_unroutable_pair() -> None:
    origins = pl.DataFrame({"demand_cell_id": ["a"], "latitude": [-40.0], "longitude": [175.0]})
    destinations = pl.DataFrame({"facility_id": ["f1"], "latitude": [-41.1], "longitude": [174.1]})
    client = LocalOsrmTableClient(
        "http://localhost:5000",
        "6.0.0",
        fetcher=lambda _url: {"code": "Ok", "distances": [[None]], "durations": [[1.0]]},
    )
    with pytest.raises(ValueError, match="unroutable"):
        client.matrix(origins, destinations)
