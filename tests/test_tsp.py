"""Tests for the pure TSP logic and the CLI group."""

import pandas as pd
from click.testing import CliRunner

from greedy_lab.cli import tsp_cli
from greedy_lab.tsp import my_cities, run_simulations, tsp


def _df(cities_coords):
    return pd.DataFrame(
        {
            "city": [c for c, _ in cities_coords],
            "latitude": [lat for _, (lat, _) in cities_coords],
            "longitude": [lon for _, (_, lon) in cities_coords],
        }
    )


def test_my_cities():
    assert my_cities("A", "B", "C") == ["A", "B", "C"]


def test_tsp_identical_coords():
    df = _df([("A", (0.0, 0.0)), ("B", (0.0, 0.0))])
    distance, route = tsp(df)
    assert distance == 0
    assert sorted(route) == ["A", "B"]


def test_run_simulations_identical_coords():
    df = _df([("A", (0.0, 0.0)), ("B", (0.0, 0.0))])
    best_distance, best_route, all_distances = run_simulations(3, df=df)
    assert best_distance == 0
    assert sorted(best_route) == ["A", "B"]
    assert all_distances == [0, 0, 0]


def test_tsp_cli_help():
    runner = CliRunner()
    result = runner.invoke(tsp_cli, ["--help"])
    assert result.exit_code == 0
    assert "simulate" in result.output
    assert "cities" in result.output
