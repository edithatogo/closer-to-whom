from pathlib import Path

import yaml

ROOT = Path(__file__).parents[2]
DIGEST = "sha256:a7091038e39a73659767f34ef2d389909b42ea80b09bd2bdca482dce2991cbad"
IMAGE = f"ghcr.io/project-osrm/osrm-backend@{DIGEST}"


def test_osrm_container_identity_is_immutable_and_consistent() -> None:
    freeze = yaml.safe_load(
        (ROOT / "data/public/routing-network-freeze.yaml").read_text(encoding="utf-8")
    )
    workflow = (ROOT / ".github/workflows/national-routing.yml").read_text(encoding="utf-8")
    compose = yaml.safe_load((ROOT / "compose.osrm.yaml").read_text(encoding="utf-8"))

    assert freeze["routing_engine"]["image"] == IMAGE
    assert freeze["routing_engine"]["container_digest"] == DIGEST
    assert freeze["road_network"]["sha256"] == (
        "2356424989e598f8eadb40cff52e9ec98da4440fdc5132f01954c24c85da4a5b"
    )
    assert f"OSRM_IMAGE: {IMAGE}" in workflow
    assert all(service["image"] == IMAGE for service in compose["services"].values())
    assert "osrm-backend:v26.7.3" not in workflow
