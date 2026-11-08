#!/usr/bin/env python
"""Shim: delegates to greedy_lab.cli.greedy_coin_cli."""

from greedy_lab.cli import greedy_coin_cli as main

if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()
