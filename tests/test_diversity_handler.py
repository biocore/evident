import os

import numpy as np
import pandas as pd
import pytest

from evident.diversity_handler import AlphaDiversityHandler


@pytest.fixture
def alpha_mock():
    fname = os.path.join(os.path.dirname(__file__), "data/metadata.tsv")
    df = pd.read_table(fname, sep="\t", index_col=0)
    return df, df["faith_pd"]


def test_alpha_div_handler(alpha_mock):
    md, faith_pd = alpha_mock
    a = AlphaDiversityHandler(faith_pd, md)
    assert a.metadata.shape == (220, 40)
    assert a.data.shape == (220, )


def test_subset_alpha_values(alpha_mock):
    md, faith_pd = alpha_mock
    a = AlphaDiversityHandler(faith_pd, md)
    b1_indices = md.query("classification == 'B1'").index
    b1_subset = a.subset_values(b1_indices)
    assert b1_subset.shape == (99, )
    np.testing.assert_almost_equal(b1_subset.mean(), 13.566,
                                   decimal=3)


class TestPower:
    def test_alpha_power_power_t(self, alpha_mock):
        md, faith_pd = alpha_mock
        a = AlphaDiversityHandler(faith_pd, md)
        calc_power = a.power_analysis(
            "classification",
            total_observations=40,
            alpha=0.05
        )
        exp_power = 0.888241
        np.testing.assert_almost_equal(calc_power, exp_power, decimal=6)

    def test_alpha_power_obs_t(self, alpha_mock):
        md, faith_pd = alpha_mock
        a = AlphaDiversityHandler(faith_pd, md)
        power = 0.888241
        calc_nobs = a.power_analysis(
            "classification",
            alpha=0.05,
            power=power
        )
        assert calc_nobs == 40

    def test_alpha_power_alpha_t(self, alpha_mock):
        md, faith_pd = alpha_mock
        a = AlphaDiversityHandler(faith_pd, md)
        power = 0.888241
        total_observations = 40
        calc_alpha = a.power_analysis(
            "classification",
            total_observations=total_observations,
            power=power
        )
        exp_alpha = 0.05
        np.testing.assert_almost_equal(calc_alpha, exp_alpha, decimal=2)
