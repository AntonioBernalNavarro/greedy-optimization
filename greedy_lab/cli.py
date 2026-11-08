"""Click CLI entry points for the lab."""

import json

import click

from greedy_lab.calculator import add
from greedy_lab.coin import greedy_coin
from greedy_lab.tsp import create_cities_dataframe, my_cities, run_simulations


def _format_change(change_cents: int, counts: dict) -> str:
    """Render a human-readable summary of the change."""
    lines = [f"Your change for ${change_cents / 100:.2f}:"]
    for name, count in counts.items():
        if count:
            plural = "" if count == 1 else "s"
            lines.append(f"{count} {name}{plural}")
    return "\n".join(lines)


@click.command()
@click.option(
    "--dollars",
    type=click.IntRange(min=0),
    default=0,
    show_default=True,
    help="Whole-dollar part of the amount.",
)
@click.option(
    "--cents",
    type=click.IntRange(0, 99),
    default=0,
    show_default=True,
    help="Cents part of the amount (0-99).",
)
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Emit the result as JSON instead of human-readable text.",
)
def greedy_coin_cli(dollars: int, cents: int, as_json: bool) -> None:
    """Return the minimum number of coins for a given change.

    Example: ./greedy_coin.py --dollars 1 --cents 50
    """
    total_cents = dollars * 100 + cents
    counts = greedy_coin(total_cents)
    if as_json:
        click.echo(json.dumps({"total_cents": total_cents, "coins": counts}))
    else:
        click.echo(_format_change(total_cents, counts))


@click.command("add")
@click.argument("a", type=int)
@click.argument("b", type=int)
def calculator_cli(a: int, b: int) -> None:
    """Add two integers and print the result.

    Example: ./main.py 2 3
    """
    click.echo(add(a, b))


@click.group()
def tsp_cli() -> None:
    """Traveling salesman simulation."""


@tsp_cli.command("cities")
@click.argument("cities", nargs=-1)
@click.option("--count", default=5, help="Number of simulations to run")
def cities_cli(cities, count):
    """Run the simulation over an explicit list of cities."""
    df = create_cities_dataframe(my_cities(*cities))
    best_distance, best_route, all_distances = run_simulations(count, df=df)
    for i, d in enumerate(all_distances):
        click.echo(f"Running similation: {i}:  Found total distance: {d}")
    click.echo(f"Shortest Distance: {best_distance}")
    click.echo(f"Cities Visited: {best_route}")


@tsp_cli.command("simulate")
@click.option("--count", default=10, help="Number of times to run the simulation.")
def simulate_cli(count):
    """Run the simulation ``count`` times over the default 20 cities."""
    best_distance, best_route, all_distances = run_simulations(count)
    for i, d in enumerate(all_distances):
        click.echo(f"Running similation: {i}:  Found total distance: {d}")
    click.echo(f"Shortest Distance: {best_distance}")
    click.echo(f"Cities Visited: {best_route}")
