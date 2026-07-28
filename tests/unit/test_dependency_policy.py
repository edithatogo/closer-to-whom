import yaml
from pathlib import Path


def test_dependabot_is_the_single_authoritative_update_system() -> None:
    with Path(".github/dependency-policy.yaml").open(encoding="utf-8") as handle:
        policy = yaml.safe_load(handle)
    assert policy["authoritative_update_system"] == "dependabot"
    assert {item["owner"] for item in policy["ecosystems"].values()} == {"dependabot"}
    assert all(
        item["automerge"] is False for item in policy["ecosystems"].values() if "automerge" in item
    )
