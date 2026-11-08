"""
Test goes here

"""

from greedy_lab.calculator import add

from click.testing import CliRunner

from greedy_lab.cli import calculator_cli


def test_add():
    assert add(1, 2) == 3


def test_calculator_cli():
    runner = CliRunner()
    result = runner.invoke(calculator_cli, ["2", "3"])
    assert result.exit_code == 0
    assert result.output.strip() == "5"
