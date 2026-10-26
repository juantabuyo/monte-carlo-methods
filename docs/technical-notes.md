# Execution and numerical conventions

The [README](../README.md) gives the installation, runner commands and results.
The default runner executes plain Python cells in a shared namespace with a
non-interactive Matplotlib backend. It is specific to this notebook, not a general
Jupyter replacement. Only run notebooks you trust. The Jupyter engine uses a real
kernel; its operation remains unverified.

Default settings are seed 20261017, a 50,000-sample cap and up to 30 repeats.
Exercises 3 and 23 retain 10 and 20 repeats. `MC_SEED`, `MC_MAX_SAMPLES` and
`MC_REPEATS` control direct notebook execution; the runner exposes corresponding
options. Figures and `results/run-summary.json` are replaced even when `--output`
names a different notebook. Save a separate copy to retain earlier outputs.

Disc comparisons count candidate points for one estimate and record integrand
evaluations separately. Repeated error measurements require multiple estimates.
Clipping a grid to a circle creates a boundary discontinuity; a smooth-rectangle
convergence rate does not automatically apply.

The largest executed tensor grid has 100,000 nodes. Dimension 10 is projected,
not allocated or timed. The high-dimensional integrand decreases towards zero
with norm, but integral behaviour also depends on domain volume. The final table
has independent reference errors only for dimension 1. Timings are single local
measurements. Finite experiments do not establish universal estimator validity
or asymptotic performance. Package versions and run settings remain recorded
with the saved summary; unpinned dependencies may resolve differently later.

## Verification on 26 October 2026

All eight existing estimator tests passed. A separate copy ran all 21 code cells
with the default seed, 50,000-sample cap and 30-repeat cap through the in-process
runner. Every numerical summary value matched the saved run; only version
fields and measured timings differed. The verification used Python 3.12.14,
NumPy 2.3.5, SciPy 1.17.0, Matplotlib 3.10.8 and nbformat 5.11.1. The committed
notebook, figures and summary were preserved.

A real Jupyter-kernel check could not start because this environment denies
both TCP and IPC kernel sockets. That is an execution-environment limitation;
this check does not establish that the Jupyter engine works. Dependencies are
unpinned, so the verification environment is recorded rather than implied to
match every future installation.
