import os

import pandas as pd

from evident import AlphaDiversityHandler
from evident import exploration as expl


def test_effect_size_by_cat():
    fname = os.path.join(os.path.dirname(__file__), "data/metadata.tsv")
    df = pd.read_table(fname, sep="\t", index_col=0)
    adh = AlphaDiversityHandler(df["faith_pd"], df)

    df = expl.effect_size_by_category(
        adh, columns=["perianal_disease", "sex", "classification",
                      "cd_behavior"]
    )
    exp_index = ["perianal_disease", "sex", "classification",
                 "cd_behavior"]
    assert (df.index == exp_index).all()

    exp_cols = ["metric", "value"]
    assert (df.columns == exp_cols).all()

    exp_metrics = ["cohens_d", "cohens_d", "cohens_d", "cohens_f"]
    assert (df["metric"] == exp_metrics).all()
