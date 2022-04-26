import os

import pandas as pd
import pytest
from skbio import DistanceMatrix

from evident.diversity_handler import (AlphaDiversityHandler,
                                       BetaDiversityHandler)

NA_VALS = ["missing: not provided", "not applicable"]


# Access these with https://stackoverflow.com/a/64348247
@pytest.fixture
def alpha_mock():
    fname = os.path.join(os.path.dirname(__file__), "data/metadata.tsv")
    df = pd.read_table(fname, sep="\t", index_col=0, na_values=NA_VALS)
    adh = AlphaDiversityHandler(df["faith_pd"], df)
    return adh


@pytest.fixture
def beta_mock():
    fname = os.path.join(os.path.dirname(__file__), "data/metadata.tsv")
    df = pd.read_table(fname, sep="\t", index_col=0, na_values=NA_VALS)
    dm_file = os.path.join(os.path.dirname(__file__),
                           "data/distance_matrix.lsmat.gz")
    dm = DistanceMatrix.read(dm_file)
    bdh = BetaDiversityHandler(dm, df)
    return bdh
