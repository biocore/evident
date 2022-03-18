import os

import numpy as np
import pandas as pd
import pytest
from skbio import DistanceMatrix

from evident.diversity_handler import (AlphaDiversityHandler,
                                       BetaDiversityHandler)
import evident._exceptions as exc


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

    def test_alpha_wrong_data(self, alpha_mock):
        data = alpha_mock.data.to_frame()

        with pytest.raises(ValueError) as exc_info:
            AlphaDiversityHandler(data, alpha_mock.metadata)

        exp_err_msg = "data must be of type pandas.Series"
        assert str(exc_info.value) == exp_err_msg

    def test_alpha_data_nan(self, alpha_mock):
        data = alpha_mock.data
        data[0] = np.nan
        data[-1] = np.nan
        with pytest.warns(UserWarning) as warn_info:
            AlphaDiversityHandler(data, alpha_mock.metadata)

        warn_msg_1 = warn_info[0].message.args[0]
        warn_msg_2 = warn_info[1].message.args[0]

        exp_warn_msg_1 = "data has 2 NAs. Dropping these values."
        exp_warn_msg_2 = (
            "Data and metadata do not have the same sample IDs. Using "
            "218 samples common to both."
        )
        assert exp_warn_msg_1 == warn_msg_1
        assert exp_warn_msg_2 == warn_msg_2


class TestBetaDiv:
    def test_init_beta_div_handler(self):
        fname = os.path.join(os.path.dirname(__file__), "data/metadata.tsv")
        df = pd.read_table(fname, sep="\t", index_col=0)
        dm_file = os.path.join(os.path.dirname(__file__),
                               "data/distance_matrix.lsmat.gz")
        dm = DistanceMatrix.read(dm_file)
        b = BetaDiversityHandler(dm, df)
        assert b.metadata.shape == (220, 40)
        assert b.data.shape == (220, 220)

    def test_subset_beta_values(self, beta_mock):
        md = beta_mock.metadata
        b1_indices = md.query("classification == 'B1'").index
        b1_subset = beta_mock.subset_values(b1_indices)

        # 99 B1 samples -> (99*98)/2 = 4851
        assert b1_subset.shape == (4851, )

    def test_beta_samples(self, beta_mock):
        md = beta_mock.metadata
        assert (md.index == beta_mock.samples).all()

    def test_beta_wrong_data(self, beta_mock):
        data = beta_mock.data.to_data_frame()

        with pytest.raises(ValueError) as exc_info:
            BetaDiversityHandler(data, beta_mock.metadata)

        exp_err_msg = "data must be of type skbio.DistanceMatrix"
        assert str(exc_info.value) == exp_err_msg


class TestPower:
    def test_alpha_power_power_t(self, alpha_mock):
        calc_power = alpha_mock.power_analysis(
            "classification",
            total_observations=40,
            alpha=0.05
        ).power
        exp_power = 0.888241
        np.testing.assert_almost_equal(calc_power, exp_power, decimal=6)

    def test_alpha_power_obs_t(self, alpha_mock):
        power = 0.888241
        calc_nobs = alpha_mock.power_analysis(
            "classification",
            alpha=0.05,
            power=power
        ).total_observations
        assert calc_nobs == 40

    def test_alpha_power_alpha_t(self, alpha_mock):
        power = 0.888241
        total_observations = 40
        calc_alpha = alpha_mock.power_analysis(
            "classification",
            total_observations=total_observations,
            power=power
        ).alpha
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

    def test_alpha_power_err_no_args(self, alpha_mock):
        with pytest.raises(exc.WrongPowerArguments) as exc_info:
            alpha_mock.power_analysis("classification")
        exp_err_msg = (
            "No arguments were provided. Exactly one of alpha, power, "
            "or total_observations must be None. Arguments: "
            "alpha = None, power = None, total_observations = None."
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

    def test_alpha_power_f(self, alpha_mock, monkeypatch):
        # Monkey patch Cohen's f calculation directly in diversity_handler
        #     instead of in _utils. Doesn't really make sense that it has
        #     to be done this way but whatever.
        # https://stackoverflow.com/a/45466846
        def mock_cohens_f(*args):
            return 0.4

        monkeypatch.setattr(
            "evident.diversity_handler.calculate_cohens_f",
            mock_cohens_f
        )
        calc_power = alpha_mock.power_analysis(
            "cd_behavior",  # 3 groups
            total_observations=60,
            alpha=0.05
        ).power
        exp_power = 0.775732
        np.testing.assert_almost_equal(calc_power, exp_power, decimal=6)

    def test_beta_power_power_t(self, beta_mock):
        calc_power = beta_mock.power_analysis(
            "classification",
            total_observations=40,
            alpha=0.05
        ).power
        exp_power = 0.404539
        np.testing.assert_almost_equal(calc_power, exp_power, decimal=6)


class TestEffectSize:
    def test_non_categorical(self, alpha_mock):
        with pytest.raises(exc.NonCategoricalColumnError) as exc_info:
            alpha_mock.calculate_effect_size("year_diagnosed")
        exp_err_msg = (
            "Column must be categorical (dtype object). 'year_diagnosed' "
            "is of type int64."
        )
        assert str(exc_info.value) == exp_err_msg

    def test_only_one_category(self, alpha_mock):
        with pytest.raises(exc.OnlyOneCategoryError) as exc_info:
            alpha_mock.calculate_effect_size("env_biome")
        exp_err_msg = (
            "Column env_biome has only one value: 'urban biome'."
        )
        assert str(exc_info.value) == exp_err_msg

    def test_difference(self, alpha_mock):
        calc_effect_size = alpha_mock.calculate_effect_size(
            "classification",
            difference=3
        )
        exp_effect_size = 0.812497
        np.testing.assert_almost_equal(calc_effect_size.effect_size,
                                       exp_effect_size, decimal=6)


class TestVectorArgsPowerAnalysis:
    def test_range(self, alpha_mock):
        obs_values = range(20, 50, 5)
        power_res = alpha_mock.power_analysis(
            column="classification",
            total_observations=obs_values,
            alpha=0.05
        )

        for vector_res, obs in zip(power_res, obs_values):
            single_res = alpha_mock.power_analysis(
                column="classification",
                total_observations=obs,
                alpha=0.05
            )
            assert single_res.power == vector_res.power

    def test_np_array(self, alpha_mock):
        obs_values = np.linspace(10, 50, 5)
        power_res = alpha_mock.power_analysis(
            column="classification",
            total_observations=obs_values,
            alpha=0.05
        )
        assert len(power_res) == 5
