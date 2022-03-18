import numpy as np
import pandas as pd
import pytest

from evident import AlphaDiversityHandler
from evident import effect_size as expl
from evident import _exceptions as exc


@pytest.mark.parametrize("mock", ["alpha_mock", "beta_mock"])
def test_effect_size_by_cat(mock, request):
    dh = request.getfixturevalue(mock)
    df = expl.effect_size_by_category(
        dh, columns=["perianal_disease", "sex", "classification",
                     "cd_behavior"]
    ).to_dataframe()

    assert ~df.isna().any().any()

    exp_index = {"perianal_disease", "sex", "classification",
                 "cd_behavior"}
    assert set(df["column"]) == exp_index

    exp_cols = ["effect_size", "metric", "column"]
    assert (df.columns == exp_cols).all()

    exp_metrics = {
        "perianal_disease": "cohens_d",
        "sex": "cohens_d",
        "classification": "cohens_d",
        "cd_behavior": "cohens_f"
    }

    def check_column_metric(column, metric):
        val = df[df["column"] == column]["metric"].item()
        assert val == exp_metrics[column]

    for k, v in exp_metrics.items():
        check_column_metric(k, v)


@pytest.mark.parametrize("mock", ["alpha_mock", "beta_mock"])
def test_pairwise_effect_size_by_cat(mock, request):
    dh = request.getfixturevalue(mock)
    df = expl.pairwise_effect_size_by_category(
        dh, columns=["perianal_disease", "sex", "classification",
                     "cd_behavior"]
    ).to_dataframe()

    assert ~df.isna().any().any()

    exp_cols = ["effect_size", "metric", "column", "group_1", "group_2"]
    assert (df.columns == exp_cols).all()

    all_grp_counts = df["column"].value_counts()
    assert all_grp_counts.loc["classification"] == 1
    assert all_grp_counts.loc["perianal_disease"] == 1
    assert all_grp_counts.loc["sex"] == 1

    cd_behavior_df = df.query("column == 'cd_behavior'")
    assert cd_behavior_df.shape == (3, 5)

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


@pytest.mark.parametrize("mock", ["alpha_mock", "beta_mock"])
def test_effect_size_by_cat_parallel(mock, request):
    dh = request.getfixturevalue(mock)

    df_1 = expl.pairwise_effect_size_by_category(
        dh,
        columns=["perianal_disease", "sex", "classification",
                 "cd_behavior"]
    ).to_dataframe()
    df_2 = expl.pairwise_effect_size_by_category(
        dh,
        columns=["perianal_disease", "sex", "classification",
                 "cd_behavior"],
        n_jobs=2
    ).to_dataframe()

    pd.testing.assert_frame_equal(df_1, df_2)


@pytest.mark.parametrize("mock", ["alpha_mock", "beta_mock"])
def test_pairwise_effect_size_by_cat_parallel(mock, request):
    dh = request.getfixturevalue(mock)

    df_1 = expl.pairwise_effect_size_by_category(
        dh,
        columns=["perianal_disease", "sex", "classification",
                 "cd_behavior"]
    ).to_dataframe()
    df_2 = expl.pairwise_effect_size_by_category(
        dh,
        columns=["perianal_disease", "sex", "classification",
                 "cd_behavior"],
        n_jobs=2
    ).to_dataframe()

    pd.testing.assert_frame_equal(df_1, df_2)


@pytest.mark.parametrize("mock", ["alpha_mock", "beta_mock"])
def test_no_cols(mock, request):
    dh = request.getfixturevalue(mock)

    with pytest.raises(ValueError) as exc_info_1:
        expl.effect_size_by_category(dh)

    with pytest.raises(ValueError) as exc_info_2:
        expl.pairwise_effect_size_by_category(dh)

    exp_err_msg = "Must provide list of columns!"
    assert str(exc_info_1.value) == str(exc_info_2.value) == exp_err_msg


def test_nan_in_cols():
    col1 = ["a", "a", np.nan, "b", "b", "b"]
    col2 = ["c", "c", "d", "d", np.nan, "c"]

    df = pd.DataFrame({"col1": col1, "col2": col2})
    df.index = [f"S{x}" for x in range(len(col1))]

    faith_vals = pd.Series([1, 3, 4, 5, 6, 6])
    faith_vals.index = df.index
    adh = AlphaDiversityHandler(faith_vals, df)
    assert not np.isnan(adh.calculate_effect_size("col1").effect_size)
    assert not np.isnan(adh.calculate_effect_size("col2").effect_size)


def test_nan_in_cols_one_one_cat():
    col1 = ["a", "a", np.nan, "b", "b", "b"]
    col2 = ["c", "c", np.nan, np.nan, np.nan, "c"]

    df = pd.DataFrame({"col1": col1, "col2": col2})
    df.index = [f"S{x}" for x in range(len(col1))]

    faith_vals = pd.Series([1, 3, 4, 5, 6, 6])
    faith_vals.index = df.index
    adh = AlphaDiversityHandler(faith_vals, df)
    assert not np.isnan(adh.calculate_effect_size("col1").effect_size)

    with pytest.raises(exc.OnlyOneCategoryError) as exc_info:
        adh.calculate_effect_size("col2")

    exp_err_msg = "Column col2 has only one value: 'c'."
    assert str(exc_info.value) == exp_err_msg
