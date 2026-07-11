from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from closer_to_whom.cli import app

runner = CliRunner()


def test_cli_schema_and_demo(tmp_path: Path) -> None:
    schema = runner.invoke(app, ["schema-registry"])
    assert schema.exit_code == 0
    assert "facility" in schema.stdout
    output = tmp_path / "demo"
    demo = runner.invoke(app, ["demo", "--output", str(output), "--seed", "42"])
    assert demo.exit_code == 0
    assert (output / "manifest.json").exists()
    verify = runner.invoke(app, ["verify", "--input-dir", str(output), "--output", str(tmp_path / "verify.json")])
    assert verify.exit_code == 0


def test_cli_doctor_and_assumptions() -> None:
    doctor = runner.invoke(app, ["doctor"])
    assert doctor.exit_code == 0
    assumptions = runner.invoke(app, ["assumptions-fingerprint"])
    assert assumptions.exit_code == 0
    assert len(assumptions.stdout.strip()) == 64
