"""Regression tests for the runner's output arguments.

A missing --output directory is reported before any computation, and --results-dir
sends the figures and run-summary.json somewhere other than the tracked results/."""
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import nbformat

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / 'run_notebook.py'


def digests(directory):
    """Content hashes, not mtimes, so a rewrite with identical bytes is still detected as a write."""
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(directory.iterdir())}


def mtimes(directory):
    return {p.name: p.stat().st_mtime_ns for p in sorted(directory.iterdir())}


def run(*arguments, timeout=240):
    return subprocess.run([sys.executable, str(RUNNER), '--max-samples', '100', '--repeats', '2', *arguments],
                          capture_output=True, text=True, timeout=timeout)


class OutputArgument(unittest.TestCase):
    def test_missing_parent_fails_fast_without_touching_results(self):
        before = mtimes(ROOT / 'results')
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / 'no-such-dir' / 'out.ipynb'
            result = run('--output', str(missing))
        self.assertEqual(result.returncode, 2)
        self.assertIn('parent directory', result.stderr)
        self.assertEqual(before, mtimes(ROOT / 'results'))

    def test_results_dir_must_be_new_or_empty(self):
        before = mtimes(ROOT / 'results')
        with tempfile.TemporaryDirectory() as directory:
            used = Path(directory) / 'used'
            used.mkdir()
            (used / 'keep.txt').write_text('earlier run')
            as_file = Path(directory) / 'file'
            as_file.write_text('not a directory')
            for target in (used, as_file):
                with self.subTest(target=target.name):
                    result = run('--output', str(Path(directory) / 'out.ipynb'), '--results-dir', str(target))
                    self.assertEqual(result.returncode, 2)
                    self.assertIn('new or empty', result.stderr)
            self.assertEqual((used / 'keep.txt').read_text(), 'earlier run')
            self.assertFalse((Path(directory) / 'out.ipynb').exists())
        self.assertEqual(before, mtimes(ROOT / 'results'))

    def test_results_dir_redirects_figures_and_summary_and_leaves_tracked_results_intact(self):
        before = digests(ROOT / 'results')
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'new' / 'results'
            output = Path(directory) / 'copy.ipynb'
            result = run('--output', str(output), '--results-dir', str(target))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn('Note:', result.stderr)
            self.assertTrue(output.is_file())
            self.assertEqual(sorted(p.name for p in target.iterdir()), sorted(before))
        self.assertEqual(before, digests(ROOT / 'results'))

    def test_output_alone_warns_that_results_are_still_replaced(self):
        # Run a copy of the runner and notebook, as scripts/run_copy.py does, so the tracked results/ is untouched.
        before = digests(ROOT / 'results')
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            for name in ('run_notebook.py', 'monte_carlo_methods.ipynb'):
                (project / name).write_bytes((ROOT / name).read_bytes())
            result = subprocess.run(
                [sys.executable, str(project / 'run_notebook.py'), '--max-samples', '100', '--repeats', '2',
                 '--output', 'copy.ipynb'], capture_output=True, text=True, timeout=240)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('Note: --output only moves the notebook', result.stderr)
            self.assertEqual(sorted(p.name for p in (project / 'results').iterdir()), sorted(before))
        self.assertEqual(before, digests(ROOT / 'results'))

    def test_failed_run_notebook_goes_to_the_chosen_results_dir(self):
        spec = importlib.util.spec_from_file_location('run_notebook_under_test', RUNNER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        notebook = nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell('raise RuntimeError("boom")')])
        before = mtimes(ROOT / 'results')
        with tempfile.TemporaryDirectory() as directory:
            project, results = Path(directory), Path(directory) / 'elsewhere' / 'results'
            with self.assertRaises(RuntimeError):
                module.execute_in_process(notebook, project, results)
            self.assertTrue((results / 'failed-run.ipynb').is_file())
        self.assertEqual(before, mtimes(ROOT / 'results'))
        self.assertFalse((ROOT / 'results' / 'failed-run.ipynb').exists())


if __name__ == '__main__':
    unittest.main()
