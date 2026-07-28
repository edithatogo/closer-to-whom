"""Command-line interface for model, verification, and handover workflows."""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Annotated, cast

import polars as pl
import typer
from rich.console import Console
from rich.table import Table

from closer_to_whom.contracts import registry_manifest
from closer_to_whom.doctor import doctor_payload
from closer_to_whom.pipeline import run_demo
from closer_to_whom.provenance import assumptions_fingerprint, write_json
from closer_to_whom.validation import validate_results

app = typer.Typer(
    name="closer-to-whom",
    help="Public-data aggregate anti-HER2 access policy model.",
    no_args_is_help=True,
    pretty_exceptions_enable=False,
)
console = Console()


def _print_json(payload: object) -> None:
    console.print_json(json.dumps(payload, default=str))


@app.command()
def doctor(
    strict: Annotated[
        bool,
        typer.Option(help="Exit non-zero when any required capability is missing."),
    ] = False,
    output: Annotated[Path | None, typer.Option(help="Optional JSON receipt path.")] = None,
) -> None:
    """Inspect core and optional local-environment capabilities."""
    payload = doctor_payload(Path.cwd())
    if output is not None:
        write_json(output, payload)
    table = Table(title="Closer to whom — environment doctor")
    table.add_column("Capability")
    table.add_column("Required")
    table.add_column("Status")
    table.add_column("Detail")
    diagnostics = cast(list[dict[str, object]], payload["diagnostics"])
    for item in diagnostics:
        table.add_row(
            str(item["diagnostic_id"]),
            "yes" if bool(item["required"]) else "no",
            "pass" if bool(item["passed"]) else "missing",
            str(item["detail"]),
        )
    console.print(table)
    if strict and not payload["ready"]:
        raise typer.Exit(code=1)


@app.command()
def demo(
    output: Annotated[Path, typer.Option(help="Output directory.")] = Path("artifacts/demo"),
    seed: Annotated[int, typer.Option(help="Deterministic simulation seed.")] = 20260711,
) -> None:
    """Run the nationwide synthetic aggregate demonstration."""
    manifest = run_demo(output, seed=seed)
    _print_json(manifest)


@app.command()
def verify(
    input_dir: Annotated[Path, typer.Option(help="Directory containing results.parquet.")] = Path(
        "artifacts/demo"
    ),
    output: Annotated[Path, typer.Option(help="Validation receipt path.")] = Path(
        "artifacts/verification/results.json"
    ),
) -> None:
    """Validate an aggregate result cube against model invariants."""
    results_path = input_dir / "results.parquet"
    if not results_path.exists():
        raise typer.BadParameter(f"Result cube does not exist: {results_path}")
    results = pl.read_parquet(results_path)
    checks = validate_results(results, output=output)
    table = Table(title="Result validation")
    table.add_column("Check")
    table.add_column("Status")
    table.add_column("Evidence")
    for check in checks:
        table.add_row(check.check_id, "pass" if check.passed else "fail", check.message)
    console.print(table)
    if any(not check.passed and check.severity == "error" for check in checks):
        raise typer.Exit(code=1)


@app.command("schema-registry")
def schema_registry(
    output: Annotated[Path | None, typer.Option(help="Optional JSON path.")] = None,
) -> None:
    """Print Arrow schema versions and fingerprints."""
    payload = registry_manifest()
    if output is not None:
        write_json(output, payload)
    _print_json(payload)


@app.command("assumptions-fingerprint")
def assumptions_command(
    directory: Annotated[Path, typer.Option(help="Assumptions directory.")] = Path("assumptions"),
) -> None:
    """Fingerprint parsed assumption files independently of YAML formatting."""
    files = tuple(directory.glob("*.yaml"))
    if not files:
        raise typer.BadParameter(f"No YAML assumption files found under {directory}")
    console.print(assumptions_fingerprint(files))


@app.command("national-summary")
def national_summary(
    directory: Annotated[
        Path, typer.Option(help="Directory containing reviewed national reports.")
    ] = Path("reports/national-analysis"),
) -> None:
    """Print the reviewed national aggregate scenario summary as JSON."""
    path = directory / "scenario_summary.json"
    if not path.exists():
        raise typer.BadParameter(f"National summary does not exist: {path}")
    _print_json(json.loads(path.read_text(encoding="utf-8")))


@app.command("space-provenance")
def space_provenance(
    path: Annotated[Path, typer.Option(help="Static Space provenance manifest.")] = Path(
        "spaces/static/provenance.json"
    ),
) -> None:
    """Print the static Space provenance manifest as JSON."""
    if not path.exists():
        raise typer.BadParameter(f"Space provenance manifest does not exist: {path}")
    _print_json(json.loads(path.read_text(encoding="utf-8")))


@app.command("national-validate")
def national_validate(
    output: Annotated[Path | None, typer.Option(help="Optional JSON receipt path.")] = None,
) -> None:
    """Validate the canonical national scientific report set and print its receipt."""
    script = Path("scripts/check_national_scientific_outputs.py")
    if not script.exists():
        raise typer.BadParameter("Run this command from the repository root")
    spec = importlib.util.spec_from_file_location("check_national_scientific_outputs", script)
    if spec is None or spec.loader is None:
        raise typer.BadParameter(f"Unable to load validator: {script}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    payload = module.validate()
    if output is not None:
        write_json(output, payload)
    _print_json(payload)


@app.command("space-build")
def space_build(
    output: Annotated[Path, typer.Option(help="Static Space output directory.")],
    revision: Annotated[str, typer.Option(help="Approved source revision embedded in the build.")],
    analysis: Annotated[
        Path, typer.Option(help="Directory containing canonical national reports.")
    ] = Path("reports/national-analysis"),
) -> None:
    """Build the static national Space from precomputed reports."""
    script = Path("scripts/build_national_static_space.py")
    if not script.exists():
        raise typer.BadParameter("Run this command from the repository root")
    spec = importlib.util.spec_from_file_location("build_national_static_space", script)
    if spec is None or spec.loader is None:
        raise typer.BadParameter(f"Unable to load builder: {script}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    built = module.build(analysis, output, revision=revision)
    _print_json({"status": "built", "output": str(built), "revision": revision})


@app.command("mojo-canary")
def mojo_canary(
    required: Annotated[
        bool,
        typer.Option(help="Treat an unavailable Mojo executable as failure."),
    ] = False,
) -> None:
    """Run the non-critical Mojo numerical canary when the toolchain is installed."""
    executable = shutil.which("mojo")
    if executable is None:
        console.print("Mojo toolchain not found; canary skipped.")
        if required:
            raise typer.Exit(code=1)
        return
    source = Path(__file__).parent / "accel/mojo/course_cost.mojo"
    result = subprocess.run([executable, str(source)], check=False, capture_output=True, text=True)
    console.print(result.stdout)
    if result.returncode != 0:
        console.print(result.stderr, style="red")
        raise typer.Exit(code=result.returncode)
    expected = 1015.2
    try:
        observed = float(result.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError) as exc:
        raise typer.BadParameter("Mojo canary did not emit a numeric final line") from exc
    if abs(observed - expected) > 1e-9:
        console.print(f"Expected {expected}, observed {observed}", style="red")
        raise typer.Exit(code=1)


@app.command("run-release-gate")
def run_release_gate() -> None:
    """Execute the maximal local release gate."""
    script = Path("scripts/release_gate.py")
    if not script.exists():
        raise typer.BadParameter("Run this command from the repository root")
    raise typer.Exit(code=subprocess.call([sys.executable, str(script)]))


if __name__ == "__main__":  # pragma: no cover
    app()
