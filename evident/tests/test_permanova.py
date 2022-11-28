import numpy as np
from evident.effect_size import effect_size_by_category


def test_permanova(beta_mock):
    mdh = beta_mock
    result_1 = mdh.calculate_effect_size("classification", permanova=True)
    result_2 = mdh.calculate_effect_size("cd_behavior", permanova=True)

    exp_1 = 0.074407
    np.testing.assert_approx_equal(exp_1, result_1.effect_size, 5)

    exp_2 = 0.081102
    np.testing.assert_approx_equal(exp_2, result_2.effect_size, 5)


def test_boot_permanova(beta_mock):
    mdh = beta_mock
    result_1 = mdh.calculate_effect_size("classification", permanova=True,
                                         bootstrap_iterations=50)
    result_2 = mdh.calculate_effect_size("cd_behavior", permanova=True,
                                         bootstrap_iterations=50)

    exp_1 = 0.074407
    np.testing.assert_approx_equal(exp_1, result_1.effect_size, 5)
    assert result_1.upper_es > result_1.effect_size
    assert result_1.lower_es < result_1.effect_size

    exp_2 = 0.081102
    np.testing.assert_approx_equal(exp_2, result_2.effect_size, 5)
    assert result_2.upper_es > result_2.effect_size
    assert result_2.lower_es < result_2.effect_size


def test_permanova_es_by_cat(beta_mock):
    mdh = beta_mock
    cols = ["classification", "cd_behavior"]
    result = effect_size_by_category(mdh, cols, permanova=True)
    result = result.to_dataframe()

    exp_1 = 0.074407
    res_1 = result.query("column == 'classification'")["effect_size"]
    np.testing.assert_approx_equal(exp_1, res_1, 5)

    exp_2 = 0.081102
    res_2 = result.query("column == 'cd_behavior'")["effect_size"]
    np.testing.assert_approx_equal(exp_2, res_2, 5)


def test_permanova_es_by_cat_boot(beta_mock):
    mdh = beta_mock
    cols = ["classification", "cd_behavior"]
    result = effect_size_by_category(mdh, cols, permanova=True,
                                     bootstrap_iterations=50)
    result = result.to_dataframe()

    exp_1 = 0.074407
    res_1 = result.query("column == 'classification'")
    np.testing.assert_approx_equal(exp_1, res_1["effect_size"], 5)
    assert res_1.upper_es.item() > res_1.effect_size.item()
    assert res_1.lower_es.item() < res_1.effect_size.item()

    exp_2 = 0.081102
    res_2 = result.query("column == 'cd_behavior'")
    np.testing.assert_approx_equal(exp_2, res_2["effect_size"], 5)
    assert res_2.upper_es.item() > res_2.effect_size.item()
    assert res_2.lower_es.item() < res_2.effect_size.item()


def test_permanova_power(beta_mock):
    mdh = beta_mock
    result_1 = mdh.power_analysis_permanova(
        "sex",
        total_observations=[25, 50, 75, 100],
        alpha=[0.01, 0.05],
        permutations=999
    ).to_dataframe()

    for alpha, _df in result_1.groupby("alpha"):
        power_vec = _df["effect_size"].to_list()
        power_vec_sorted = sorted(power_vec)
        assert power_vec == power_vec_sorted
