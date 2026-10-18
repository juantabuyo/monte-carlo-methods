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
