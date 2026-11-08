"""Click CLI entry points for the lab."""

import json

import click

from greedy_lab.calculator import add
from greedy_lab.coin import greedy_coin


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
