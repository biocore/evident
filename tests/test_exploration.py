import pytest

from evident import exploration as expl


@pytest.mark.parametrize("mock", ["alpha_mock", "beta_mock"])
def test_effect_size_by_cat(mock, request):
    dh = request.getfixturevalue(mock)
    df = expl.effect_size_by_category(
        dh, columns=["perianal_disease", "sex", "classification",
                     "cd_behavior"]
    )

    assert ~df.isna().any().any()

    exp_index = {"perianal_disease", "sex", "classification",
                 "cd_behavior"}
    assert set(df.index) == exp_index

    exp_cols = ["metric", "value"]
    assert (df.columns == exp_cols).all()

    assert df.loc["perianal_disease"]["metric"] == "cohens_d"
    assert df.loc["sex"]["metric"] == "cohens_d"
    assert df.loc["classification"]["metric"] == "cohens_d"
    assert df.loc["cd_behavior"]["metric"] == "cohens_f"


@pytest.mark.parametrize("mock", ["alpha_mock", "beta_mock"])
def test_pairwise_effect_size_by_cat(mock, request):
    dh = request.getfixturevalue(mock)
    df = expl.pairwise_effect_size_by_category(
        dh, columns=["perianal_disease", "sex", "classification",
                     "cd_behavior"]
    )

    assert ~df.isna().any().any()

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


@pytest.mark.parametrize("mock", ["alpha_mock", "beta_mock"])
def test_no_cols(mock, request):
    dh = request.getfixturevalue(mock)

    with pytest.raises(ValueError) as exc_info_1:
        expl.effect_size_by_category(dh)

    with pytest.raises(ValueError) as exc_info_2:
        expl.pairwise_effect_size_by_category(dh)

    exp_err_msg = "Must provide list of columns!"
    assert str(exc_info_1.value) == str(exc_info_2.value) == exp_err_msg
