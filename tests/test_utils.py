import numpy as np

from evident import _utils as utils

def test_pooled_std():
    a = [1, 2, 3, 4, 5, 6]
    b = [2, 5, 3, 6, 8, 9]
    pooled_std = utils.calculate_pooled_stdev(a, b)
    exp_val = 2.345208
    np.testing.assert_almost_equal(exp_val, pooled_std, decimal=6)
