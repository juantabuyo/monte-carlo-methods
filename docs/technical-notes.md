# Execution and numerical conventions

The [README](../README.md) gives installation, safe run commands and the principal
results. The runner executes plain Python cells in a shared namespace with a
non-interactive Matplotlib backend. It is specific to this notebook and does not
emulate IPython display hooks. Only execute notebooks whose code you trust.

## Preserve earlier outputs

Use `python scripts/run_copy.py runs/new-name` from the project root. The wrapper
requires a new destination, copies the existing notebook and runner, and calls
the copied runner through Python's `runpy`. There are no duplicated estimators.
The output folder contains the execution copy and its new results.

Calling `python run_notebook.py` directly has different file-writing behaviour:
it replaces the tracked notebook, figures and `results/run-summary.json`.
`--output another.ipynb` alone changes only the notebook destination: figures and
the summary are still replaced, and the runner prints a note saying so. Add
`--results-dir runs/other/results` to send the figures, `run-summary.json` and any
`failed-run.ipynb` to a new or empty directory (an existing, non-empty one is
refused before anything runs). The copy wrapper remains the simplest way to retain
earlier outputs. The `--output` notebook's parent must already exist; this is
checked before any computation, with exit code 2.

## Settings and environment

Default settings are seed 20261017, a 50,000-sample cap and up to 30 repeats.
Exercises 3 and 23 retain caps of 10 and 20 repeats. `MC_SEED`, `MC_MAX_SAMPLES`
and `MC_REPEATS` control direct notebook execution; the runner exposes the same
settings as options. The tensor grid through dimension 5 is not reduced by the
random-sample cap.

The tested environments use CPython 3.12.2 on macOS and CPython 3.12.14, with
pip 26.2.2, NumPy 2.5.4, SciPy 1.18.1, Matplotlib 3.11.2, nbformat 5.11.1,
nbclient 0.11.0 and ipykernel 7.4.0. `constraints-tested.txt` fixes these six direct
project dependencies for repeatable installation. It is not a lock of every transitive dependency and
does not promise compatibility with untested Python versions.

The saved 17 October results used Matplotlib 3.10.8, as recorded in their summary.
The macOS execution on 26 October used the environment above, seed 20261017,
10,000 maximum samples and five repeats. All 21 code cells executed sequentially,
with execution counts 1–21 and no error outputs. The eight original unit tests
passed and `pip check` reported no dependency conflicts. This was a separate,
reduced experiment; it did not replace or numerically reproduce the larger one.
Floating-point results, sampling streams and timings can depend on versions,
execution order and hardware.

### Reproduce the displayed figures

After installation, run from the project folder, choosing a new destination:

```bash
python scripts/run_copy.py runs/reduced-macos --seed 20261017 --max-samples 10000 --repeats 5 --engine in-process
```

The figures appear at `runs/reduced-macos/results/pi-convergence.png` and
`runs/reduced-macos/results/proposal-comparison.png`. The README uses unchanged
copies of those outputs from the 26 October macOS run, stored under descriptive
names in `docs/images/`. The run generated all ten project figures; only these
two are selected for the README. No values, axes or image pixels were edited.
The new `results/run-summary.json` in that execution folder identifies the
settings and environment. Its `prepared_on` value describes the code's prepared
version, not the execution date.

For an existing Jupyter installation, open the notebook with the project folder
as its working directory. The optional runner engine is:

```bash
python scripts/run_copy.py runs/kernel-check --max-samples 10000 --repeats 5 --engine jupyter
```

Its kernel/client dependencies are included, but a notebook editor is not.
A real-kernel run remains unverified; successful sequential execution does not
establish that the kernel integration works. Direct notebook execution writes
to its working directory's `results/` unless `MC_RESULTS_DIR` names another
directory (the runner sets it from `--results-dir`), so make a copy first.

## Interpreting costs and errors

Disc comparisons count candidate points for one estimate and record integrand
evaluations separately. Repeated error measurements cost multiple estimates.
Clipping a grid to a circle creates a boundary discontinuity, so a convergence
rate for a smooth rectangle does not automatically apply.

The largest executed tensor grid has 100,000 nodes. Dimension 10 is projected,
not allocated or timed. The high-dimensional integrand tends towards zero with
norm, but the integral also depends on increasing domain volume. The final table
has independent reference errors only for dimension 1. Finite experiments do not
establish universal estimator validity or asymptotic performance.

## Separate default-settings check

The project documentation records a separate check on 26 October 2026 using
Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0, Matplotlib 3.10.8 and nbformat 5.11.1.
It reports that all eight tests passed and all 21 code cells ran with the default
seed, 50,000-sample cap and 30-repeat cap. Every numerical summary value matched
the saved experiment; version fields and hardware-dependent timings differed.
The committed notebook, figures and summary were preserved.

That reported check used a different environment from the reduced macOS run
pictured in the README. These are separate executions with different sample
and repeat counts. The documented Jupyter attempt could not start because
kernel sockets were unavailable; it does not establish that the real-kernel
engine works.
