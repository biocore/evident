import numpy as np
import pandas as pd
import pytest

from evident import utils
from evident.diversity_handler import AlphaDiversityHandler


def test_listify():
    a = np.array([1, 2, 3])
    np.testing.assert_equal(utils._listify(a), a)

    b = range(10)
    assert utils._listify(b) == range(10)

    c = 5
    assert utils._listify(c) == [5]

    d = [1, 2, 3]
    assert utils._listify(d) == d


def test_check_sample_overlap():
    md = pd.DataFrame.from_dict({
        "a": [1, 2, 3, 4, 5],
        "b": ["A", "B", "C", "D", "E"]
    })
    md.index = [f"S{i+1}" for i in range(5)]

    alpha_div = pd.Series(
        [6, 7, 8, 9, 10],
        index=[f"S{i+2}" for i in range(5)]
    )
    with pytest.warns(UserWarning) as warn_info:
        AlphaDiversityHandler(alpha_div, md)
    exp_msg = (
        "Data and metadata do not have the same sample IDs. Using 4 samples "
        "common to both."
    )
    assert warn_info[0].message.args[0] == exp_msg
