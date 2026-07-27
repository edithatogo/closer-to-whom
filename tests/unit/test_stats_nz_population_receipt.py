import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).parents[2]
RECEIPT = ROOT / "data/public/receipts/input-freeze/candidate.statsnz-population-estimates.json"


def test_frozen_population_query_is_the_successful_sa2_capture() -> None:
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    url = receipt["data_url"]
    selector = urlparse(url).path.rsplit("/", 1)[-1]
    dimensions = selector.split(".")
    area_codes = dimensions[-1].split("+")

    assert dimensions[:3] == ["2025", "3", "999999"]
    assert len(area_codes) == 2314
    assert len(set(area_codes)) == 2314
    assert area_codes[0] == "100100"
    assert area_codes[-1] == "364000"
    assert not ({"01", "02", "03", "RC9999", "NIRC", "SIRC"} & set(area_codes))
    assert receipt["latest_sa2_capture"]["run"] == "30068260658"
    assert receipt["latest_sa2_capture"]["rows"] == 2313
    assert receipt["latest_sa2_capture"]["request_selector_count"] == 2314
    assert receipt["latest_sa2_capture"]["materialized_unique_sa2_codes"] == 2313
