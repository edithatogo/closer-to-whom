"""Hugging Face Docker Space serving precomputed aggregate result cubes only."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import polars as pl

CLAIM_BOUNDARY = (
    "Public-data policy simulation. Not a forecast of individual care, actual service use, "
    "capacity, waiting time, or clinical outcomes."
)


def _load_frames(result_dir: Path) -> tuple[pl.DataFrame, pl.DataFrame]:
    summary_path = result_dir / "scenario-summary.parquet"
    equity_path = result_dir / "equity-ethnicity.parquet"
    if not summary_path.exists() or not equity_path.exists():
        from closer_to_whom.pipeline import run_demo

        run_demo(result_dir)
    return pl.read_parquet(summary_path), pl.read_parquet(equity_path)


def create_app(result_dir: Path | None = None) -> Any:
    """Create a Dash application without exposing raw or row-level inputs."""
    try:
        import plotly.graph_objects as go
        from dash import Dash, Input, Output, dcc, html
    except ImportError as exc:  # pragma: no cover - optional deployment dependency
        raise RuntimeError("Install closer-to-whom[dashboard] to run the dashboard") from exc

    directory = result_dir or Path(os.environ.get("CTW_RESULT_DIR", "artifacts/demo"))
    summary, equity = _load_frames(directory)
    scenario_options = sorted(summary.get_column("scenario_id").unique().to_list())
    application = Dash(__name__)
    application.title = "Closer to whom?"
    application.layout = html.Main(
        [
            html.H1("Closer to whom?"),
            html.P(CLAIM_BOUNDARY, id="claim-boundary"),
            html.Label("Scenario"),
            dcc.Dropdown(
                id="scenario",
                options=[{"label": value, "value": value} for value in scenario_options],
                value=scenario_options[0],
                clearable=False,
            ),
            dcc.Graph(id="travel-chart"),
            dcc.Graph(id="equity-chart"),
            html.P(
                "Every displayed value is precomputed from aggregate or synthetic inputs; no "
                "individual locations are served."
            ),
        ]
    )

    @application.callback(
        Output("travel-chart", "figure"),
        Output("equity-chart", "figure"),
        Input("scenario", "value"),
    )
    def update(selected: str) -> tuple[Any, Any]:
        selected_summary = summary.filter(pl.col("scenario_id") == selected)
        travel = go.Figure(
            data=[
                go.Bar(
                    x=selected_summary.get_column("pathway_id").to_list(),
                    y=selected_summary.get_column("mean_course_travel_minutes").to_list(),
                    name="Course travel minutes",
                )
            ]
        )
        travel.update_layout(title="Expected course travel minutes — aggregate simulation")

        selected_equity = equity.filter(pl.col("scenario_id") == selected)
        equity_figure = go.Figure()
        for pathway in sorted(selected_equity.get_column("pathway_id").unique().to_list()):
            subset = selected_equity.filter(pl.col("pathway_id") == pathway)
            equity_figure.add_bar(
                x=subset.get_column("ethnicity").to_list(),
                y=subset.get_column("mean_course_travel_minutes").to_list(),
                name=pathway,
            )
        equity_figure.update_layout(
            barmode="group",
            title="Area-level equity stratification — ecological interpretation only",
        )
        return travel, equity_figure

    return application


app = create_app()
server = app.server


if __name__ == "__main__":  # pragma: no cover
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "7860")), debug=False)
