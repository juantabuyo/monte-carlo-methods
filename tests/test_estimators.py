"""Focused estimator and counter checks; no notebook experiment is run here."""

import ast
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import numpy as np
from scipy.special import erf


def notebook_functions():
    """Load only function definitions, avoiding duplicated implementations."""
    notebook = json.loads((Path(__file__).resolve().parents[1] /
                           'monte_carlo_methods.ipynb').read_text())
    definitions = []
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':
            source = cell['source']
            if isinstance(source, list):
                source = ''.join(source)
            definitions.extend(node for node in ast.parse(source).body
                               if isinstance(node, ast.FunctionDef))
    namespace = {'np': np}
    exec(compile(ast.Module(body=definitions, type_ignores=[]),
                 'notebook_function_definitions', 'exec'), namespace)
    return namespace


FUNCTIONS = notebook_functions()


class EstimatorChecks(unittest.TestCase):
    def setUp(self):
        np.random.seed(12345)

    def test_uniform_constant_and_reference_integrals(self):
        uniform = FUNCTIONS['uniform_integral']
        self.assertAlmostEqual(uniform(lambda x: np.ones_like(x)*3, -2, 2, 50), 12)
        self.assertLess(abs(uniform(lambda x: x*x, 0, 1, 50000)-1/3), 0.01)
        square = FUNCTIONS['uniform_integral_2d']
        self.assertAlmostEqual(square(lambda x, y: np.ones_like(x), 0, 2, -1, 2, 50), 6)
        self.assertLess(abs(square(lambda x, y: x*x+y*y, 0, 1, 0, 1, 50000)-2/3), 0.01)

    def test_hit_or_miss_bounds_and_left_rectangle(self):
        hit = FUNCTIONS['hit_or_miss_integral']
        self.assertEqual(hit(lambda x: np.zeros_like(x), 0, 2, 3, 100), 0)
        self.assertEqual(hit(lambda x: np.ones_like(x)*3, 0, 2, 3, 100), 6)
        self.assertAlmostEqual(FUNCTIONS['left_rectangle_rule'](lambda x: x, 0, 1, 10), 0.45)

    def test_importance_constant_weights_and_invalid_density(self):
        importance = FUNCTIONS['importance_sampling']
        value = importance(lambda x: 6*x, lambda x: 2*x,
                           lambda n: np.sqrt(np.random.uniform(0, 1, n)), 1000)
        self.assertAlmostEqual(value, 3)
        with self.assertRaises(ValueError):
            importance(lambda x: x, lambda x: np.zeros_like(x), np.ones, 4)

    def test_truncated_gaussian_support_and_normalisation(self):
        FUNCTIONS.update(sigma_is=0.05, a12=-1, b12=1)
        samples = FUNCTIONS['truncated_gaussian_samples'](1000)
        self.assertEqual(samples.shape, (1000,))
        self.assertTrue(np.all(np.abs(samples) <= 1))
        normaliser = 0.05*np.sqrt(2*np.pi)*erf(1/(0.05*np.sqrt(2)))
        value = FUNCTIONS['importance_sampling'](
            lambda x: np.exp(-x*x/(2*0.05**2)),
            lambda x: np.exp(-x*x/(2*0.05**2))/normaliser,
            FUNCTIONS['truncated_gaussian_samples'], 1000)
        self.assertAlmostEqual(value, normaliser, places=14)

    def test_disc_counts_and_known_area_are_distinct(self):
        evaluated = []
        def constant(x, y):
            evaluated.append(len(x))
            return np.ones_like(x)
        estimate, candidates, accepted = FUNCTIONS['disc_integral'](constant, 2, 1000, True)
        self.assertAlmostEqual(estimate, 4*np.pi)
        self.assertEqual(candidates, 1000)
        self.assertEqual(accepted, evaluated[0])
        self.assertGreater(accepted, 0)
        self.assertLess(accepted, candidates)
        self.assertEqual(FUNCTIONS['disc_area_from_hits'](2, 750, 1000), 12)
        grid_estimate, grid_candidates, grid_evaluations = FUNCTIONS['disc_midpoint_rule'](constant, 1, 10)
        self.assertEqual(grid_candidates, 100)
        self.assertEqual(grid_evaluations, evaluated[-1])
        self.assertAlmostEqual(grid_estimate, (2/10)**2*grid_evaluations)

    def test_empty_disc_sample_has_explicit_error(self):
        with patch.object(np.random, 'uniform', return_value=np.array([0.99])):
            with self.assertRaisesRegex(ValueError, 'No candidates'):
                FUNCTIONS['disc_integral'](lambda x, y: x, 1, 1)

    def test_dimension_integrand_and_sample_variance(self):
        with patch.object(np.random, 'uniform', return_value=np.array([[1., 1.]])):
            self.assertAlmostEqual(FUNCTIONS['dimension_integral'](2, 1), 4/17)
        mean, variance = FUNCTIONS['sample_statistics']([1, 2, 3])
        self.assertEqual(mean, 2)
        self.assertEqual(variance, 1)
        with self.assertRaises(ValueError):
            FUNCTIONS['sample_statistics']([1])

    def test_seeded_reproducibility(self):
        first = FUNCTIONS['uniform_integral'](np.exp, 0, 1, 100)
        np.random.seed(12345)
        second = FUNCTIONS['uniform_integral'](np.exp, 0, 1, 100)
        self.assertEqual(first, second)


if __name__ == '__main__':
    unittest.main()
