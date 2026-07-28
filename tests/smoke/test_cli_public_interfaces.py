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
