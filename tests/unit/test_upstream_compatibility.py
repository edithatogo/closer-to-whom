from runpy import run_path

validate = run_path(
    "scripts/check_upstream_compatibility.py",
    run_name="upstream_compatibility_test",
)["validate"]


def test_optional_upstream_contracts_are_valid() -> None:
    assert validate() == []
