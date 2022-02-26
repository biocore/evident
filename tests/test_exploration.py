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
    exp_index = {"perianal_disease", "sex", "classification",
                 "cd_behavior"}
    assert set(df.index) == exp_index

    exp_cols = ["metric", "value"]
    assert (df.columns == exp_cols).all()

    assert df.loc["perianal_disease"]["metric"] == "cohens_d"
    assert df.loc["sex"]["metric"] == "cohens_d"
    assert df.loc["classification"]["metric"] == "cohens_d"
    assert df.loc["cd_behavior"]["metric"] == "cohens_f"


def test_pairwise_effect_size_by_cat():
    fname = os.path.join(os.path.dirname(__file__), "data/metadata.tsv")
    df = pd.read_table(fname, sep="\t", index_col=0)
    adh = AlphaDiversityHandler(df["faith_pd"], df)

    df = expl.pairwise_effect_size_by_category(
        adh, columns=["perianal_disease", "sex", "classification",
                      "cd_behavior"]
    )

    exp_cols = ["column", "group_1", "group_2", "cohens_d"]
    assert (df.columns == exp_cols).all()

    all_grp_counts = df["column"].value_counts()
    assert all_grp_counts.loc["classification"] == 1
    assert all_grp_counts.loc["perianal_disease"] == 1
    assert all_grp_counts.loc["sex"] == 1

    cd_behavior_df = df.query("column == 'cd_behavior'")
    assert cd_behavior_df.shape == (3, 4)

    cd_behavior_melt_df = cd_behavior_df.melt(
        value_vars=["group_1", "group_2"]
    )
    grp_counts = cd_behavior_melt_df["value"].value_counts()
    grps = [
        "Non-stricturing, non-penetrating (B1)",
        "Stricturing (B2)",
        "Penetrating (B3)"
    ]
    for grp in grps:
        assert grp_counts.loc[grp] == 2
