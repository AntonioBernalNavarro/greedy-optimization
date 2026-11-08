#!/usr/bin/env python
"""Shim: delegates to greedy_lab.cli.tsp_cli."""

from greedy_lab.cli import tsp_cli as cli

if __name__ == "__main__":
    cli()
