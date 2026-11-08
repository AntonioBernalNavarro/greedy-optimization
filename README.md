# Greedy Optimization Lab — Coursera MLOps C2

Solution to **Lab 4** of the Coursera MLOps course. This repository
contains two command-line tools, a small library, and the analysis
required by the lab.

- **`greedy_coin.py`** — computes the minimum number of US coins for a
  given amount of change (Part A of the lab).
- **`tsp.py`** — runs a randomized traveling-salesman simulation over
  20 US cities, using Nominatim for geocoding and `geopy` for
  distances (Part B of the lab).
- **`greedy_lab/`** — pure-Python library modules used by both CLIs.
  No I/O, no `print`, no `click`. The scripts at the repository root
  are thin shims; the logic and the click commands live here.

The full analysis of what was changed and why is in
[`REFLECTION.md`](REFLECTION.md).

---

## Requirements

### Python version

This branch targets **Python 3.12**. The `requirements.txt` has been
updated accordingly (see *Dependency changes* below).

### Dependency changes vs. the original lab

The `requirements.txt` shipped with the course was pinned to versions
from 2022 that do not provide prebuilt **wheels** for CPython 3.12.
Installing it on Python 3.12 fails during the build phase with errors
such as:

```
ModuleNotFoundError: No module named 'pkg_resources'
ERROR: Failed to build 'pandas' when getting requirements to build wheel
```

The pinned versions affected were `pandas==1.5.0`, `numpy==1.23.3`,
`scikit-learn==1.1.2`, `matplotlib==3.6.0`, `torch==1.12.1`,
`tensorflow==2.10.0`, `onnx==1.12.0` and `protobuf==3.16.0`.

This branch (commit `a9d4d50`, *build: update dependencies for Python
3.12 compatibility*) makes the following changes:

- **Bumped to versions with 3.12 wheels** — `pandas>=2.2.2`,
  `numpy>=1.26.4`, `scikit-learn>=1.4.0`, `matplotlib>=3.8.0`,
  `torch>=2.2.0`, `tensorflow>=2.16.0`, `onnx>=1.16.0`, and the
  HuggingFace stack (`transformers>=4.40.0`, `datasets>=2.18.0`,
  `tokenizers>=0.19.0`).
- **`protobuf` pinned to `>=4.25.0,<5`** to keep `mlflow`, `onnx` and
  `transformers` mutually compatible (they currently do not support
  protobuf 5.x).
- **Removed `databricks==0.2` and `databricks-cli==0.17.3`** —
  obsolete, not compatible with 3.12, and superseded by
  `databricks-sdk`, which `mlflow` installs automatically.
  `databricks-sql-connector` was bumped to `>=3.0.0`.
- **`jupyter` left unpinned** so `pip` resolves the latest compatible
  release for 3.12.

The exact versions in this branch are in [`requirements.txt`](requirements.txt).
If you need byte-identical reproducibility, run `pip freeze > requirements.lock`
after a successful install.

---

## Setup

```bash
make install
```

or, without `make`:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Optional: install the package in editable mode to get console scripts
(see *Console scripts* below).

```bash
pip install -e .
```

---

## Project structure

```
.
├── greedy_coin.py            # shim -> greedy_lab.cli:greedy_coin_cli
├── main.py                   # shim -> greedy_lab.cli:calculator_cli
├── tsp.py                    # shim -> greedy_lab.cli:tsp_cli
├── greedy_lab/
│   ├── __init__.py
│   ├── calculator.py         # add / subtract / multiply / divide
│   ├── cli.py                # all click commands and groups
│   ├── coin.py               # greedy_coin(change_cents) -> dict
│   └── tsp.py                # my_cities / create_cities_dataframe / tsp / run_simulations
├── tests/
│   ├── test_calculator.py    # tests for greedy_lab.calculator and its CLI
│   ├── test_greedy_coin.py   # tests for greedy_lab.coin and greedy_coin CLI
│   └── test_tsp.py           # deterministic tests for greedy_lab.tsp
├── scripts/
│   ├── repeat.sh
│   └── setup.sh
├── REFLECTION.md             # answers to the four lab reflection questions
├── pyproject.toml            # project metadata, console scripts, tool config
├── Makefile
├── Dockerfile
├── requirements.txt
└── README.md
```

The root scripts (`greedy_coin.py`, `main.py`, `tsp.py`) are kept as
three-line shims so the lab's original command-line contract
(`python greedy_coin.py ...`, `python tsp.py simulate`) keeps working.
Everything else — logic and click commands — lives under `greedy_lab/`.

---

## Part A — Greedy change CLI

### Usage

The original positional form (`python greedy_coin.py 1.50`) has been
**replaced** by two flags, as required by task A.2.

```bash
# 1 dollar 50 cents
python greedy_coin.py --dollars 1 --cents 50
# Your change for $1.50:
# 6 quarters

# 30 cents — demonstrates the float-drift bug fixed in this branch
python greedy_coin.py --cents 30
# Your change for $0.30:
# 1 quarter
# 1 nickel

# Same as the first example, but machine-readable
python greedy_coin.py --dollars 1 --cents 50 --json
# {"total_cents": 150, "coins": {"quarter": 6, "dime": 0, "nickel": 0, "penny": 0}}
```

### Flags

| Flag        | Type             | Default | Description                                    |
|-------------|------------------|---------|------------------------------------------------|
| `--dollars` | integer `>= 0`   | `0`     | Whole-dollar part of the amount.               |
| `--cents`   | integer `0..99`  | `0`     | Cents part of the amount.                      |
| `--json`    | flag             | off     | Emit JSON instead of the human-readable text.  |

Invalid values (`--cents 100`, `--dollars -1`) are rejected by Click
at parse time, before any computation runs.

### What changed vs. the original

1. **Input moved from a positional float to two `IntRange` flags.**
   The amount is unambiguous and validation is done by the CLI layer.
2. **The core logic was extracted into `greedy_lab/coin.py`** and now
   operates on **integer cents** rather than floats. This removes a
   real bug: the original implementation returned 29 cents for
   `$0.30` because `0.30 - 0.25 == 0.04999999999999999` (strictly
   less than `0.05`), so the loop skipped the nickel.
3. **`--json` output was added** so the tool can be consumed by other
   scripts without screen-scraping the text output.
4. **A full test suite was added** (`tests/test_greedy_coin.py`, 12
   tests) covering the pure core, the CLI flags, range validation,
   singular/plural formatting, and a regression test for the `$0.30`
   bug.

Detailed reasoning in [`REFLECTION.md` § A](REFLECTION.md).

---

## Part B — Traveling salesman

### Usage

```bash
# Run the simulation with the default count (10)
python tsp.py simulate

# Run a specific number of simulations
python tsp.py simulate --count 1000

# Run against an explicit list of cities
python tsp.py cities "New York" "Boston" "Chicago" "Miami" --count 100
```

The command prints the best tour found across all runs and the
corresponding total distance (in miles).

### Geocoding cache

The 20 default city coordinates are cached in
`city_coords_cache.json` after the first run. This is required by
Nominatim's usage policy (cache results, ≤ 1 request/second) and
avoids rate limits during sweeps. The cache file is gitignored and is
regenerated automatically if missing.

### Optimal number of simulations

A sweep over `count = 10, 100, 1,000, 5,000` (with cache warm) is
documented in [`REFLECTION.md` § B](REFLECTION.md). Short version: the
knee of the curve is around **`count ≈ 1,000`**; beyond that the best
distance improves by ~10% per 5× more samples. Low counts are
dominated by the randomness of `random.shuffle`, which has no seed.

---

## Console scripts

`pip install -e .` exposes three console scripts via
`[project.scripts]` in `pyproject.toml`:

| Command        | Equivalent to                |
|----------------|------------------------------|
| `greedy-coin`  | `python greedy_coin.py`      |
| `greedy-add`   | `python main.py`             |
| `greedy-tsp`   | `python tsp.py`              |

Example:

```bash
pip install -e .
greedy-coin --dollars 1 --cents 50
greedy-add 2 3
greedy-tsp simulate --count 3
```

The root shims are kept for the lab's original command-line contract;
the console scripts are the canonical interface for anything outside
the lab.

---

## Testing and quality

```bash
make test       # pytest + coverage
make lint       # pylint (root + greedy_lab/)
make format     # black (root + greedy_lab/ + tests/)
```

Current status on this branch:

- **18 tests pass** across `test_calculator.py`, `test_greedy_coin.py`
  and `test_tsp.py`.
- Coverage: `greedy_lab/coin.py` **100%**, `greedy_lab/cli.py` **77%**,
  `greedy_lab/tsp.py` **62%** (the uncovered lines are the Nominatim
  geocoding block, which requires network access and is intentionally
  not unit-tested).
- `pylint`: **10.00 / 10**.

## Docker

```bash
make container-lint
```

runs `hadolint` against the `Dockerfile`.

---

## Original lab tasks

Preserved here for reference. The commands below reflect the
*original* state of the repository at `main`, not the current branch.

> **A. Run the greedy change command-line tool**
>
> 1. Run the greedy change command-line tool: `python greedy_coin.py 1.50`
> 2. Change the code to have a flag for dollars and flag for cents,
>    i.e., `--dollars` and `--cents`.
>
> **Reflection question:** Is this version of the command-line tool
> more robust against errors?
>
> **Reflection question:** What could you build to enhance this
> script? Do it and add it to your portfolio.
>
> **B. Run the traveling salesman algorithm**
>
> 1. Run the traveling salesman algorithm: `python tsp.py simulate`
> 2. What is the optimal number of simulations to run?

Both reflection questions and the TSP analysis are answered in
[`REFLECTION.md`](REFLECTION.md).

---

## Authors and origin

- **Original lab**: [Coursera MLOps C2 — Lab 4: Greedy Optimization](https://github.com/nogibjj/Coursera-MLOps-C2-lab4-greedy-optimization),
  by [Noah Gift](https://github.com/nogibjj) / Pragmatic AI Labs.
- **This fork**: [Antonio Bernal Navarro](https://github.com/AntonioBernalNavarro/greedy-optimization),
  with the changes documented in [`REFLECTION.md`](REFLECTION.md):
  `--dollars`/`--cents`/`--json` flags, integer-cents core, Python 3.12
  dependency bump, Nominatim cache, package layout, console scripts.

## License

Distributed under the terms of the [`LICENSE`](LICENSE) file included
in this repository, inherited from the original lab.