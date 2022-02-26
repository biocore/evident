import numpy as np

from evident import stats


def test_calc_pooled_std_two_groups():
    a = [1, 2, 3, 4, 5, 6]
    b = [2, 5, 3, 6, 8, 9]

    calc_pooled_std = stats.calculate_pooled_stdev(a, b)
    exp_pooled_std = 2.345208
    np.testing.assert_almost_equal(exp_pooled_std, calc_pooled_std, decimal=6)


def test_calc_pooled_std_three_groups():
    a = [1, 2, 3, 4, 5, 6]
    b = [2, 5, 3, 6, 8, 9]
    c = [0, 2, 2, 5, 1, 4]

    calc_pooled_std = stats.calculate_pooled_stdev(a, b, c)
    exp_pooled_std = 2.195955
    np.testing.assert_almost_equal(exp_pooled_std, calc_pooled_std, decimal=6)


def test_calc_cohens_d():
    a = [1, 2, 3, 4, 5, 6]
    b = [2, 5, 3, 6, 8, 9]

    calc_cohen_d = stats.calculate_cohens_d(a, b)
    exp_cohen_d = 0.852803
    np.testing.assert_almost_equal(exp_cohen_d, calc_cohen_d, decimal=6)


def test_calc_cohens_f_two_groups():
    # Cohen's f = 0.5 * Cohen's d
    a = [1, 2, 3, 4, 5, 6]
    b = [2, 5, 3, 6, 8, 9]

    exp_cohen_f = 0.852803 / 2
    calc_cohen_f = stats.calculate_cohens_f(a, b)
    np.testing.assert_almost_equal(exp_cohen_f, calc_cohen_f, decimal=6)
