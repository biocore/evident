import numpy as np


def test_permanova(beta_mock):
    mdh = beta_mock
    result_1 = mdh.calculate_effect_size("classification", permanova=True)
    result_2 = mdh.calculate_effect_size("cd_behavior", permanova=True)

    exp_1 = 0.074407
    np.testing.assert_approx_equal(exp_1, result_1.effect_size, 5)

    exp_2 = 0.081102
    np.testing.assert_approx_equal(exp_2, result_2.effect_size, 5)
