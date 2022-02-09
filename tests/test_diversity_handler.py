import os

import pandas as pd
import pytest

from evident.diversity_handler import AlphaDiversityHandler


@pytest.fixture
def alpha_mock():
    fname = os.path.join(os.path.dirname(__file__), "data/metadata.tsv")
    df = pd.read_table(fname, sep="\t", index_col=0)
    return df, df["faith_pd"]


class TestInitialization:
    def test_alpha_div_handler(self, alpha_mock):
        md, faith_pd = alpha_mock
        a = AlphaDiversityHandler(faith_pd, md)
        assert a.metadata.shape == (220, 40)
        assert a.data.shape == (220, )
