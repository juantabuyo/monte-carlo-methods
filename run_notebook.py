"""Execute the Monte Carlo notebook from start to finish without external services."""

import argparse
import base64
import contextlib
import io
import os
from pathlib import Path
import sys
import traceback

import nbformat


def execute_in_process(notebook, project):
    """Execute plain Python cells in order, capturing actual prints and figures.

    This notebook has no magics, interactive widgets or top-level expressions
    that rely on IPython display hooks. A shared namespace preserves its normal
    sequential semantics. This is not a simulation of a Jupyter kernel.
    """
    import matplotlib
    matplotlib.use('Agg')
    from matplotlib import pyplot as plt

    namespace = {'__name__': '__main__'}
    original_show = plt.show
    working_directory = Path.cwd()
    count = 0
    try:
        os.chdir(project)
        for index, cell in enumerate(notebook.cells):
            if cell.cell_type != 'code':
                continue
            count += 1
            cell.execution_count = count
            cell.outputs = []
            stdout, stderr = io.StringIO(), io.StringIO()

            def flush_streams():
                for name, stream in [('stdout', stdout), ('stderr', stderr)]:
                    value = stream.getvalue()
                    if value:
                        cell.outputs.append(nbformat.v4.new_output('stream', name=name, text=value))
                        stream.seek(0)
                        stream.truncate(0)

            def capture_figure(*args, **kwargs):
                flush_streams()
                for number in plt.get_fignums():
                    buffer = io.BytesIO()
                    plt.figure(number).savefig(buffer, format='png', dpi=100, bbox_inches='tight')
                    cell.outputs.append(nbformat.v4.new_output(
                        'display_data', data={'image/png': base64.b64encode(buffer.getvalue()).decode('ascii')},
                        metadata={}))

            plt.show = capture_figure
            try:
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    exec(compile(cell.source, f'monte_carlo_methods.ipynb:cell-{index}', 'exec'), namespace)
            except Exception as error:
                flush_streams()
                cell.outputs.append(nbformat.v4.new_output('error', ename=type(error).__name__,
                                    evalue=str(error), traceback=traceback.format_exc().splitlines()))
                nbformat.write(notebook, project/'results/failed-run.ipynb')
                raise
            flush_streams()
            print(f'Executed cell {index} ({count} code cells).', file=sys.stderr)
    finally:
        plt.show = original_show
        plt.close('all')
        os.chdir(working_directory)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=int, default=20261017)
    parser.add_argument('--max-samples', type=int, default=50000)
    parser.add_argument('--repeats', type=int, default=30)
    parser.add_argument('--engine', choices=['in-process', 'jupyter'], default='in-process',
                        help='Sequential Python (default) or a Jupyter kernel')
    parser.add_argument('--output', default='monte_carlo_methods.ipynb',
                        help='Output notebook path, relative to the project directory')
    args = parser.parse_args()
    if args.max_samples < 100 or args.repeats < 2:
        parser.error('Use at least 100 samples and two repeats.')
    project = Path(__file__).resolve().parent
    os.environ.update(MC_SEED=str(args.seed), MC_MAX_SAMPLES=str(args.max_samples),
                      MC_REPEATS=str(args.repeats))
    notebook = nbformat.read(project / 'monte_carlo_methods.ipynb', as_version=4)
    nbformat.validate(notebook)
    for cell in notebook.cells:
        if cell.cell_type == 'code':
            cell.outputs = []
            cell.execution_count = None
    if args.engine == 'jupyter':
        from nbclient import NotebookClient
        NotebookClient(notebook, timeout=240, kernel_name='python3',
                       resources={'metadata': {'path': str(project)}}).execute()
    else:
        execute_in_process(notebook, project)
    notebook.metadata['execution'] = {'engine': args.engine, 'seed': args.seed,
                                     'sample_cap': args.max_samples, 'repeat_cap': args.repeats}
    nbformat.validate(notebook)
    output = project / args.output
    nbformat.write(notebook, output)
    print(f'Executed all code cells and saved {output.name}.')
    print('Regenerated figures and summary in results/.')


if __name__ == '__main__':
    main()
