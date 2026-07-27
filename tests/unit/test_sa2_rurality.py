import importlib.util
import sys
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "materialize_sa2_rurality",
    Path(__file__).parents[2] / "scripts" / "materialize_sa2_rurality.py",
)
assert _SPEC and _SPEC.loader
_MODULE = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _MODULE
_SPEC.loader.exec_module(_MODULE)
classify_point = _MODULE.classify_point


def test_classifies_one_official_polygon() -> None:
    point = {
        "geography_code": "100100",
        "routing_point_id": "SA2-100100",
        "latitude": -35.0,
        "longitude": 174.0,
    }
    payload = {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [[173.0, -36.0], [175.0, -36.0], [175.0, -34.0], [173.0, -34.0], [173.0, -36.0]]
            ],
        },
        "properties": {
            "UR2023_V1_00": "1013",
            "UR2023_V1_00_NAME": "Other rural Far North District",
            "IUR2023_V1_00": "22",
            "IUR2023_V1_00_NAME": "Rural other",
        },
    }
    result = classify_point(point, [payload])
    assert result["rurality_status"] == "matched_official_urban_rural_2023"
    assert result["indicator_name"] == "Rural other"


@pytest.mark.parametrize(
    ("features", "expected"),
    [
        ([], "unknown_no_polygon"),
        (
            [
                {
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [[173, -36], [175, -36], [175, -34], [173, -34], [173, -36]]
                        ],
                    }
                },
                {
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [[173, -36], [175, -36], [175, -34], [173, -34], [173, -36]]
                        ],
                    }
                },
            ],
            "unknown_ambiguous",
        ),
    ],
)
def test_preserves_unmatched_or_ambiguous_as_unknown(features: list[dict], expected: str) -> None:
    point = {
        "geography_code": "100100",
        "routing_point_id": "SA2-100100",
        "latitude": -35.0,
        "longitude": 174.0,
    }
    result = classify_point(point, features)
    assert result["rurality_status"] == expected
    assert result["indicator_name"] is None
