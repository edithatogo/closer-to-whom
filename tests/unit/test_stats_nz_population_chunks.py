import importlib.util
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "fetch_stats_nz_population_chunks",
    Path(__file__).parents[2] / "scripts" / "fetch_stats_nz_population_chunks.py",
)
assert _SPEC and _SPEC.loader
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)


def test_split_request_preserves_order_and_query() -> None:
    prefix, codes, query = _MODULE._split_request(
        "https://example.test/data/2025.3.999999.A+B?format=csv"
    )
    assert prefix.endswith("2025.3.999999")
    assert codes == ["A", "B"]
    assert query == "format=csv"
