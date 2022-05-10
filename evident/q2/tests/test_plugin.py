import os

import numpy as np
import pandas as pd
import pytest
from qiime2 import Artifact, Metadata
from qiime2.plugins import evident


@pytest.fixture(scope="module")
def alpha_artifact():
    fname = os.path.join(os.path.dirname(__file__), "data/test_alpha_div.qza")
    return Artifact.load(fname)


@pytest.fixture(scope="module")
def beta_artifact():
    fname = os.path.join(os.path.dirname(__file__), "data/test_beta_div.qza")
    return Artifact.load(fname)


@pytest.fixture(scope="module")
def metadata():
    fname = os.path.join(os.path.dirname(__file__), "data/test_metadata.qza")
    return Metadata.load(fname)


@pytest.fixture(scope="module")
def metadata_w_data():
    fname = os.path.join(os.path.dirname(__file__), "data/test_metadata.qza")
    metadata = Metadata.load(fname).to_dataframe()
    fname = os.path.join(os.path.dirname(__file__), "data/test_alpha_div.qza")
    metadata["alpha_div"] = Artifact.load(fname).view(pd.Series)
    return Metadata(metadata)


@pytest.fixture(scope="module")
def es_results(alpha_artifact, metadata_w_data):
    res = evident.methods.univariate_effect_size_by_category(
        sample_metadata=metadata_w_data,
        data_column="alpha_div",
        group_columns=["classification", "cd_behavior"]
    ).effect_size_results
    return res


@pytest.fixture(scope="module")
def pa_results(alpha_artifact, metadata_w_data):
    res = evident.methods.univariate_power_analysis(
        sample_metadata=metadata_w_data,
        data_column="alpha_div",
        group_column="classification",
        alpha=[0.01, 0.05, 0.1],
        total_observations=[20, 30, 40]
    ).power_analysis_results
    return res


def test_alpha_pa(alpha_artifact, metadata_w_data):
    evident.methods.univariate_power_analysis(
        sample_metadata=metadata_w_data,
        data_column="alpha_div",
        group_column="classification",
        alpha=[0.01, 0.05],
        power=[0.8]
    ).power_analysis_results.view(pd.DataFrame)


def test_beta_pa(beta_artifact, metadata):
    evident.methods.multivariate_power_analysis(
        data=beta_artifact,
        sample_metadata=metadata,
        group_column="classification",
        alpha=[0.05],
        power=[0.8]
    )


def test_univariate_effect_size_by_cat(alpha_artifact, metadata_w_data):
    exp_cols = ["effect_size", "metric", "column"]
    non_pairwise = evident.methods.univariate_effect_size_by_category(
        sample_metadata=metadata_w_data,
        data_column="alpha_div",
        group_columns=["classification", "cd_behavior"]
    ).effect_size_results.view(pd.DataFrame)
    assert non_pairwise.shape == (2, 3)
    assert (non_pairwise.columns == exp_cols).all()

    exp_cols = ["effect_size", "metric", "column", "group_1", "group_2"]
    pairwise = evident.methods.univariate_effect_size_by_category(
        sample_metadata=metadata_w_data,
        data_column="alpha_div",
        group_columns=["classification", "cd_behavior"],
        pairwise=True
    ).effect_size_results.view(pd.DataFrame)
    assert pairwise.shape == (4, 5)
    assert (pairwise.columns == exp_cols).all()


def test_multivariate_effect_size_by_cat(beta_artifact, metadata):
    non_pairwise = evident.methods.multivariate_effect_size_by_category(
        data=beta_artifact,
        sample_metadata=metadata,
        group_columns=["classification", "cd_behavior"]
    ).effect_size_results.view(pd.DataFrame)
    assert non_pairwise.shape == (2, 3)
    assert (non_pairwise.columns == ["effect_size", "metric", "column"]).all()

    pairwise = evident.methods.multivariate_effect_size_by_category(
        data=beta_artifact,
        sample_metadata=metadata,
        group_columns=["classification", "cd_behavior"],
        pairwise=True
    ).effect_size_results.view(pd.DataFrame)
    assert pairwise.shape == (4, 5)
    exp_cols = ["effect_size", "metric", "column", "group_1", "group_2"]
    assert (pairwise.columns == exp_cols).all()


def test_univariate_effect_size_by_cat_parallel(alpha_artifact,
                                                metadata_w_data):
    non_pairwise = evident.methods.univariate_effect_size_by_category(
        sample_metadata=metadata_w_data,
        data_column="alpha_div",
        group_columns=["classification", "cd_behavior"],
        n_jobs=2
    ).effect_size_results.view(pd.DataFrame)
    assert non_pairwise.shape == (2, 3)
    assert (non_pairwise.columns == ["effect_size", "metric", "column"]).all()

    pairwise = evident.methods.univariate_effect_size_by_category(
        sample_metadata=metadata_w_data,
        data_column="alpha_div",
        group_columns=["classification", "cd_behavior"],
        pairwise=True,
        n_jobs=2
    ).effect_size_results.view(pd.DataFrame)
    assert pairwise.shape == (4, 5)
    exp_cols = ["effect_size", "metric", "column", "group_1", "group_2"]
    assert (pairwise.columns == exp_cols).all()


def test_multivariate_effect_size_by_cat_parallel(beta_artifact, metadata):
    non_pairwise = evident.methods.multivariate_effect_size_by_category(
        data=beta_artifact,
        sample_metadata=metadata,
        group_columns=["classification", "cd_behavior"],
        n_jobs=2
    ).effect_size_results.view(pd.DataFrame)
    assert non_pairwise.shape == (2, 3)
    assert (non_pairwise.columns == ["effect_size", "metric", "column"]).all()

    pairwise = evident.methods.multivariate_effect_size_by_category(
        data=beta_artifact,
        sample_metadata=metadata,
        group_columns=["classification", "cd_behavior"],
        pairwise=True,
        n_jobs=2
    ).effect_size_results.view(pd.DataFrame)
    assert pairwise.shape == (4, 5)
    exp_cols = ["effect_size", "metric", "column", "group_1", "group_2"]
    assert (pairwise.columns == exp_cols).all()


def test_visualize_es_results(es_results):
    evident.visualizers.visualize_results(results=es_results)


def test_visualize_pa_results(pa_results):
    evident.visualizers.visualize_results(results=pa_results)


def test_plot_power_curve(pa_results):
    evident.visualizers.plot_power_curve(
        power_analysis_results=pa_results,
        target_power=0.6,
        style="alpha"
    )


def test_alpha_pa_repeated():
    data_dict = {
        "S1": {"T1": 45, "T2": 50, "T3": 55},
        "S2": {"T1": 42, "T2": 42, "T3": 45},
        "S3": {"T1": 36, "T2": 41, "T3": 43},
        "S4": {"T1": 39, "T2": 35, "T3": 40},
        "S5": {"T1": 51, "T2": 55, "T3": 59},
        "S6": {"T1": 44, "T2": 49, "T3": 56}
    }
    long_data = (
        pd.DataFrame.from_dict(data_dict)
        .reset_index()
        .rename(columns={"index": "group"})
        .melt(id_vars="group", var_name="subject", value_name="diversity")
    )
    long_data.index = [f"SAMP{x}" for x in range(long_data.shape[0])]
    long_data.index.name = "sampleid"
    long_data["diversity"] = long_data["diversity"].astype(float)

    rng = np.random.default_rng()
    num_samples = 6
    num_groups = 3
    long_data["cov"] = rng.choice(["A", "B"], size=num_samples*num_groups)
    bad_col = rng.choice(
        ["C", "D", np.nan],
        size=num_samples*num_groups,
        p=[0.25, 0.25, 0.5]
    )
    long_data["bad_col"] = bad_col

    exp_power_dict = {
        (2, -0.5): 0.11387136147153543,
        (2, 0): 0.13648071042423104,
        (2, 0.5): 0.18720958942768118,
        (4, -0.5): 0.42616026628041437,
        (4, 0): 0.5662936523912177,
        (4, 0.5): 0.8221488475653276,
        (5, -0.5): 0.5891411383898337,
        (5, 0): 0.7508935036261379,
        (5, 0.5): 0.9517932434077899
    }

    exp_cols = {
        "alpha", "total_observations", "power", "effect_size", "subjects",
        "measurements", "epsilon", "correlation", "total_observations",
        "metric", "column"
    }
    results, = evident.methods.univariate_power_analysis_repeated_measures(
        sample_metadata=Metadata(long_data),
        data_column="diversity",
        individual_id_column="subject",
        state_column="group",
        subjects=[2, 4, 5],
        measurements=[10],
        correlation=[-0.5, 0, 0.5],
        epsilon=[0.1],
        alpha=[0.05]
    )

    results_df = results.view(pd.DataFrame)
    assert set(results_df.columns) == exp_cols

    for i, row in results_df.iterrows():
        key = row["subjects"], row["correlation"]
        np.testing.assert_almost_equal(
            exp_power_dict[key],
            row["power"],
            decimal=5
        )
    evident.visualizers.visualize_results(results=results)


def test_univariate_bad_data(alpha_artifact, metadata, metadata_w_data):
    with pytest.raises(ValueError) as exc_info:
        evident.methods.univariate_power_analysis(
            sample_metadata=metadata,
            data_column="greninja",
            group_column="classification",
            alpha=[0.01, 0.05],
            power=[0.8]
        )
    exp_err_msg = "greninja not found in sample metadata."
    assert str(exc_info.value) == exp_err_msg

    with pytest.raises(ValueError) as exc_info:
        evident.methods.univariate_power_analysis(
            sample_metadata=metadata_w_data,
            data_column="ibd_subtype",
            group_column="classification",
            alpha=[0.01, 0.05],
            power=[0.8]
        )
    exp_err_msg = "Values in data_column must be numeric."
    assert str(exc_info.value) == exp_err_msg
