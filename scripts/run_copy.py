"""Run the existing notebook runner in a new directory, preserving saved results."""

import argparse
from pathlib import Path
import runpy
import shutil
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="New directory for the execution copy")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--max-samples", type=int)
    parser.add_argument("--repeats", type=int)
    parser.add_argument("--engine", choices=("in-process", "jupyter"))
    args = parser.parse_args()
    runner_args = []
    for option in ("seed", "max_samples", "repeats", "engine"):
        value = getattr(args, option)
        if value is not None:
            runner_args.extend(["--" + option.replace("_", "-"), str(value)])
    project = Path(__file__).resolve().parents[1]
    output = args.directory.resolve()
    if output.exists():
        parser.error("Choose a new directory; existing runs are never overwritten.")
    output.mkdir(parents=True)
    for name in ("run_notebook.py", "monte_carlo_methods.ipynb"):
        shutil.copy2(project / name, output / name)
    runner = output / "run_notebook.py"
    original_argv = sys.argv
    try:
        sys.argv = [str(runner), *runner_args]
        runpy.run_path(str(runner), run_name="__main__")
    finally:
        sys.argv = original_argv


if __name__ == "__main__":
    main()
