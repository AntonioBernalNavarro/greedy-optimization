"""Shim: delegates to greedy_lab.cli.calculator_cli."""

from greedy_lab.cli import calculator_cli as main

if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()
