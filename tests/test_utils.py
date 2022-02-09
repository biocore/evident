import numpy as np

from evident import _utils as utils

def test_calc_pooled_std():
    a = [1, 2, 3, 4, 5, 6]
    b = [2, 5, 3, 6, 8, 9]

    calc_pooled_std = utils.calculate_pooled_stdev(a, b)
    exp_pooled_std = 2.345208
    np.testing.assert_almost_equal(exp_pooled_std, calc_pooled_std, decimal=6)


def test_calc_cohen_d():
    a = [1, 2, 3, 4, 5, 6]
    b = [2, 5, 3, 6, 8, 9]

    calc_cohen_d = utils.calculate_cohens_d(a, b)
    exp_cohen_d = 0.852803
    np.testing.assert_almost_equal(exp_cohen_d, calc_cohen_d, decimal=6)
