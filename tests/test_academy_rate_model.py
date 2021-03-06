"""Test the AcademyRateModel class and its related functions"""
import unittest
import numpy as np

from pyesg import AcademyRateProcess
from pyesg.academy_rate_model import interpolate, perturb, AcademyRateModel
from pyesg.datasets import load_academy_sample_scenario


class TestAcademyRateModel(unittest.TestCase):
    """Test the AcademyRateModel class"""

    @classmethod
    def setUpClass(cls):
        cls.model = AcademyRateModel()
        cls.test_scenario = load_academy_sample_scenario()

    def test_interpolate(self):
        """Ensure the interpolate function works as expected"""
        # the function expects multiple short rates and long rates
        short_rate = np.full((1, 1), 0.01)
        long_rate = np.full((1, 1), 0.03)
        maturities = np.array([0.5, 1.0, 5.0, 10.0, 20.0, 30.0])
        actual = interpolate(short_rate, long_rate, interpolated_maturities=maturities)
        expected = np.array([[[0.00765, 0.01, 0.021208, 0.026554, 0.03, 0.031191]]])
        self.assertIsNone(np.testing.assert_array_almost_equal(actual, expected))

    def test_perturb(self):
        """Ensure the pertubtation function works as expected"""
        # this function essentially grades the scenario from the starting yield curve up
        # to the scenario value over the first projection year of the scenarios. We'll
        # test this by making sure this happens as expected for some dummy scenarios.
        yield_curve = np.array([0.005, 0.015, 0.025, 0.035, 0.045])
        scenarios = np.array([[[0.01, 0.02, 0.03, 0.04, 0.05]] * 3])
        actual = perturb(scenarios=scenarios, n_steps=2, yield_curve=yield_curve)
        expected = [
            [0.005, 0.015, 0.025, 0.035, 0.045],
            [0.0075, 0.0175, 0.0275, 0.0375, 0.0475],
            [0.01, 0.02, 0.03, 0.04, 0.05],
        ]
        expected = np.array([expected])
        self.assertIsNone(np.testing.assert_array_almost_equal(actual, expected))

    def test_scenario_shape(self):
        """Ensure the scenarios method produces the right shape"""
        scenarios = self.model.scenarios(dt=1 / 12, n_scenarios=10, n_steps=30)
        self.assertEqual(scenarios.shape, (10, 31, 10))

    def test_scenario_values(self):
        """Compare the pyesg model vs. a single scenario from the AAA Excel model"""
        model = AcademyRateModel(volatility=self.test_scenario["volatility"])
        model.yield_curve = self.test_scenario["yield_curve"]
        model.process = AcademyRateProcess(**self.test_scenario["process_parameters"])
        scenario = model.scenarios(
            dt=self.test_scenario["dt"],
            n_scenarios=self.test_scenario["n_scenarios"],
            n_steps=self.test_scenario["n_steps"],
            floor=self.test_scenario["floor"],
            random_state=self.test_scenario["random_state"],
        )
        self.assertIsNone(
            np.testing.assert_array_almost_equal(
                self.test_scenario["sample_scenario"], scenario[0]
            )
        )
