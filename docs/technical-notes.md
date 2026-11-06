# Running notes and numerical conventions

The [README](../README.md) introduces the estimators and displayed results.
All 24 exercises are in `monte_carlo_methods.ipynb`; the separate coursework
finance extension is not part of this repository.

## Running the notebook

From the project root, use a new destination to retain the existing outputs:

```bash
python scripts/run_copy.py runs/new-name
```

The wrapper copies the notebook and runner, then calls the copied runner through
Python's `runpy`. It does not contain another set of estimators. Default settings
are seed 20261017, a 50,000-sample cap and up to 30 repeats. Exercises 3 and 23
retain caps of 10 and 20 repeats. The tensor grid through dimension 5 is not
reduced by the random-sample cap.

For the smaller experiment used by the README figures:

```bash
python scripts/run_copy.py runs/reduced --seed 20261017 --max-samples 10000 --repeats 5 --engine in-process
```

The two figures are written to `runs/reduced/results/pi-convergence.png` and
`runs/reduced/results/proposal-comparison.png`. The run also produces the other
project figures, an executed notebook and `results/run-summary.json` inside
the new destination. The README uses the existing saved copies under
`docs/images/`; running this command does not replace them.

Use Python 3.12 with the packages in `requirements.txt` and
`constraints-tested.txt`. The constraints fix the direct project dependencies,
not every transitive dependency. Saved run summaries record their own package
versions. Floating-point results, random streams and timings can depend on
versions, execution order and hardware. On Windows, activate the environment
with `.venv\Scripts\activate` instead of the macOS/Linux `source` command.

### Optional Jupyter engine

The default in-process engine runs ordinary Python cells in a shared namespace
with a non-interactive Matplotlib backend. It is specific to this notebook and
does not emulate IPython display hooks.

An alternative uses a Jupyter kernel:

```bash
python scripts/run_copy.py runs/kernel-example --max-samples 10000 --repeats 5 --engine jupyter
```

Kernel/client dependencies are included, but a notebook editor is not. Real
Jupyter-kernel execution has not been checked; direct Python execution does not
validate that integration. Opening the notebook directly writes results in its
working directory unless `MC_RESULTS_DIR` specifies another folder. Work on a
copy if you want to retain the saved outputs.

### Direct runner and output paths

Calling `python run_notebook.py` directly replaces the tracked notebook, figures
and `results/run-summary.json`. `--output another.ipynb` alone changes only the
notebook destination: figures and the summary still use the normal results
directory.

Add `--results-dir runs/other/results` to send figures, the summary and any
`failed-run.ipynb` to a new or empty directory. A non-empty results directory is
rejected before execution. The `--output` notebook's parent directory must
already exist. The copy wrapper is simpler when keeping earlier runs.

`MC_SEED`, `MC_MAX_SAMPLES` and `MC_REPEATS` control direct notebook execution;
the runner exposes the same settings as options.

## Interpreting costs and errors

The reduced figures and the larger saved `results/` experiment use different
sample and repeat counts. Keep their settings separate when comparing numbers.
For exercise 8, the reduced experiment's mean adjacent log–log slope is −0.370;
the theoretical standard-error reference exponent is −0.5. The scaled reference
line in the π plot is not an error bound or proof of convergence.

Disc comparisons count candidate points for one estimate and integrand
evaluations separately. Repeated error measurements require multiple estimates.
The disc estimator uses the known area; a separate acceptance calculation
estimates area without π. Clipping a grid to a circle introduces a boundary
discontinuity, so a convergence rate for a smooth rectangle does not
automatically apply.

Importance sampling needs adequate support and finite weight variance. A
proposal proportional to the integrand is an explanatory ideal: knowing its
normalising constant already gives the integral.

Vectorised work and memory scale as `O(n*d)`. The largest executed tensor grid
has 100,000 nodes; dimension 10 is projected rather than allocated or timed.
The high-dimensional integrand tends towards zero with norm, but the integral
also depends on increasing domain volume. The final table has independent
reference errors only for dimension 1. Finite experiments and local timings do
not establish universal estimator accuracy or asymptotic performance.
