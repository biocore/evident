import os

import numpy as np
import pandas as pd
import pytest

from evident.diversity_handler import AlphaDiversityHandler
import evident.exceptions as exc


@pytest.fixture
def alpha_mock():
    fname = os.path.join(os.path.dirname(__file__), "data/metadata.tsv")
    df = pd.read_table(fname, sep="\t", index_col=0)
    adh = AlphaDiversityHandler(df["faith_pd"], df)
    return adh


class TestAlphaDiv:
    def test_init_alpha_div_handler(self):
        fname = os.path.join(os.path.dirname(__file__), "data/metadata.tsv")
        df = pd.read_table(fname, sep="\t", index_col=0)
        a = AlphaDiversityHandler(df["faith_pd"], df)
        assert a.metadata.shape == (220, 40)
        assert a.data.shape == (220, )

    def test_subset_alpha_values(self, alpha_mock):
        md = alpha_mock.metadata
        b1_indices = md.query("classification == 'B1'").index
        b1_subset = alpha_mock.subset_values(b1_indices)
        assert b1_subset.shape == (99, )
        np.testing.assert_almost_equal(b1_subset.mean(), 13.566,
                                       decimal=3)

    def test_alpha_samples(self, alpha_mock):
        md = alpha_mock.metadata
        assert (md.index == alpha_mock.samples).all()


class TestPower:
    def test_alpha_power_power_t(self, alpha_mock):
        calc_power = alpha_mock.power_analysis(
            "classification",
            total_observations=40,
            alpha=0.05
        )
        exp_power = 0.888241
        np.testing.assert_almost_equal(calc_power, exp_power, decimal=6)

    def test_alpha_power_obs_t(self, alpha_mock):
        power = 0.888241
        calc_nobs = alpha_mock.power_analysis(
            "classification",
            alpha=0.05,
            power=power
        )
        assert calc_nobs == 40

    def test_alpha_power_alpha_t(self, alpha_mock):
        power = 0.888241
        total_observations = 40
        calc_alpha = alpha_mock.power_analysis(
            "classification",
            total_observations=total_observations,
            power=power
        )
        exp_alpha = 0.05
        np.testing.assert_almost_equal(calc_alpha, exp_alpha, decimal=2)

    def test_alpha_power_err_all_args(self, alpha_mock):
        with pytest.raises(exc.WrongPowerArguments) as exc_info:
            alpha_mock.power_analysis(
                "classification",
                total_observations=40,
                alpha=0.05,
                power=0.8
            )
        exp_err_msg = (
            "All arguments were provided. Exactly one of alpha, power, "
            "or total_observations must be None. Arguments: "
            "alpha = 0.05, power = 0.8, total_observations = 40."
        )
        assert str(exc_info.value) == exp_err_msg

    def test_alpha_power_err_more_args(self, alpha_mock):
        with pytest.raises(exc.WrongPowerArguments) as exc_info:
            alpha_mock.power_analysis(
                "classification",
                power=0.8
            )
        exp_err_msg = (
            "More than 1 argument was provided. Exactly one of alpha, power, "
            "or total_observations must be None. Arguments: "
            "alpha = None, power = 0.8, total_observations = None."
        )
        assert str(exc_info.value) == exp_err_msg

    def test_alpha_power_non_categorical(self, alpha_mock):
        with pytest.raises(exc.NonCategoricalColumnError) as exc_info:
            alpha_mock.power_analysis(
                "year_diagnosed",
                alpha=0.05,
                power=0.8
            )
        exp_err_msg = (
            "Column must be categorical (dtype object). 'year_diagnosed' "
            "is of type int64."
        )
        assert str(exc_info.value) == exp_err_msg

    def test_alpha_power_only_one_cat(self, alpha_mock):
        with pytest.raises(exc.OnlyOneCategoryError) as exc_info:
            alpha_mock.power_analysis(
                "env_biome",
                alpha=0.05,
                power=0.8
            )
        exp_err_msg = (
            "Column env_biome has only one value: 'urban biome'."
        )
        assert str(exc_info.value) == exp_err_msg
