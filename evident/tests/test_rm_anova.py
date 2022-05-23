import numpy as np
import pandas as pd
import pytest

from evident.data_handler import RepeatedMeasuresUnivariateDataHandler
from evident.stats import calculate_eta_squared, calculate_rm_anova_power


@pytest.fixture
def rm_alpha_mock():
    # Use modified data from tinyurl.com/ycktzet3
    data_dict = {
        "S1": {"T1": 45, "T2": 50, "T3": 55},
        "S2": {"T1": 42, "T2": 42, "T3": 45},
        "S3": {"T1": 36, "T2": 41, "T3": 43},
        "S4": {"T1": 39, "T2": 35, "T3": 40},
        "S5": {"T1": 51, "T2": 55, "T3": 59},
        "S6": {"T1": 44, "T2": 49, "T3": 56}
    }
    long_data = (
        pd.DataFrame.from_dict(data_dict)
        .reset_index()
        .rename(columns={"index": "group"})
        .melt(id_vars="group", var_name="subject", value_name="values")
    )

    rng = np.random.default_rng()
    num_samples = 6
    num_groups = 3
    long_data["cov"] = rng.choice(["A", "B"], size=num_samples*num_groups)
    bad_col = rng.choice(
        ["C", "D", np.nan],
        size=num_samples*num_groups,
        p=[0.25, 0.25, 0.5]
    )
    long_data["bad_col"] = bad_col
    rmadh = RepeatedMeasuresUnivariateDataHandler(
        data=long_data["values"],
        metadata=long_data.drop(columns=["values"]),
        individual_id_column="subject",
    )
    return rmadh


def test_calc_eta_squared(rm_alpha_mock):
    wide_data = pd.pivot_table(
        pd.concat([rm_alpha_mock.metadata, rm_alpha_mock.data], axis=1),
        index="subject",
        columns="group",
        values="values"
    )
    calc_eta_sq = calculate_eta_squared(wide_data)
    np.testing.assert_almost_equal(calc_eta_sq, 0.715, decimal=3)


def test_calc_effect_size(rm_alpha_mock):
    result = rm_alpha_mock.calculate_effect_size("group")
    np.testing.assert_almost_equal(result.effect_size, 0.715, decimal=3)
    assert result.metric == "eta_squared"
    assert result.column == "group"


def test_eta_squared_missing_vals(rm_alpha_mock):
    with pytest.raises(ValueError) as exc_info:
        rm_alpha_mock.calculate_effect_size("bad_col")

    exp_err_msg = (
        "Cannot calculate effect size of repeated measures with missing "
        "values."
    )
    assert str(exc_info.value) == exp_err_msg


def test_calculate_rm_anova_power():
    calc_power = calculate_rm_anova_power(
        subjects=10,
        measurements=5,
        effect_size=0.3,
        threshold=0.01,
        correlation=0.1,
        epsilon=1
    )
    np.testing.assert_almost_equal(calc_power, 0.8806256734819309)

    calc_power = calculate_rm_anova_power(
        subjects=100,
        measurements=2,
        effect_size=0.02,
        threshold=0.01,
        correlation=-0.8,
        epsilon=0.2
    )
    np.testing.assert_almost_equal(calc_power, 0.058864331610035125)


def test_single_power_analysis(rm_alpha_mock):
    # Calculated expected with pingouin
    exp_power = 0.6362084728045014
    result = rm_alpha_mock.power_analysis(
        state_column="group",
        subjects=2,
        measurements=10,
        alpha=0.05,
        correlation=0.0,
        epsilon=0.5
    )
    np.testing.assert_almost_equal(result.power, exp_power, decimal=5)


def test_bulk_power_analysis(rm_alpha_mock):
    exp_power_dict = {
        (2, -0.5): 0.11387136147153543,
        (2, 0): 0.13648071042423104,
        (2, 0.5): 0.18720958942768118,
        (4, -0.5): 0.42616026628041437,
        (4, 0): 0.5662936523912177,
        (4, 0.5): 0.8221488475653276,
        (5, -0.5): 0.5891411383898337,
        (5, 0): 0.7508935036261379,
        (5, 0.5): 0.9517932434077899
    }
    results = rm_alpha_mock.power_analysis(
        state_column="group",
        subjects=[2, 4, 5],
        measurements=10,
        alpha=0.05,
        correlation=[-0.5, 0, 0.5],
        epsilon=0.1
    ).to_dataframe()

    assert set(results.columns) == {
        "alpha", "total_observations", "power", "effect_size", "subjects",
        "measurements", "epsilon", "correlation", "total_observations",
        "metric", "column"
    }
    for i, row in results.iterrows():
        key = row["subjects"], row["correlation"]
        np.testing.assert_almost_equal(
            exp_power_dict[key],
            row["power"],
            decimal=5
        )
