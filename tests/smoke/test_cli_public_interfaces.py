import json
from pathlib import Path

from typer.testing import CliRunner

from closer_to_whom.cli import app


def test_national_summary_cli_is_machine_readable() -> None:
    result = CliRunner().invoke(app, ["national-summary"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "materialized_source_backed_candidate_network_comparison"


def test_space_provenance_cli_is_machine_readable() -> None:
    result = CliRunner().invoke(app, ["space-provenance"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["aggregate_only"] is True


def test_national_validate_cli_is_machine_readable(tmp_path: Path) -> None:
    receipt = tmp_path / "national-validation.json"
    result = CliRunner().invoke(app, ["national-validate", "--output", str(receipt)])
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "passed"
    assert len(payload["report_names"]) == 9
    assert json.loads(receipt.read_text(encoding="utf-8"))["status"] == "passed"


def test_space_build_cli_writes_static_bundle(tmp_path: Path) -> None:
    result = CliRunner().invoke(
        app,
        ["space-build", "--output", str(tmp_path / "space"), "--revision", "test-revision"],
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "built"
    assert (tmp_path / "space" / "index.html").exists()
    assert (tmp_path / "space" / "aggregate-reports.json").exists()


def test_mojo_canary_is_optional_when_toolchain_is_absent() -> None:
    result = CliRunner().invoke(app, ["mojo-canary"])
    assert result.exit_code == 0
