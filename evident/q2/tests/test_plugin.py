import os

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
def es_results(alpha_artifact, metadata):
    res = evident.methods.alpha_effect_size_by_category(
        alpha_diversity=alpha_artifact,
        sample_metadata=metadata,
        columns=["classification", "cd_behavior"]
    ).effect_size_results
    return res


@pytest.fixture(scope="module")
def pa_results(alpha_artifact, metadata):
    res = evident.methods.alpha_power_analysis(
        alpha_diversity=alpha_artifact,
        sample_metadata=metadata.get_column("cd_behavior"),
        alpha=[0.01, 0.05, 0.1],
        total_observations=[20, 30, 40]
    ).power_analysis_results
    return res


def test_alpha_pa(alpha_artifact, metadata):
    evident.methods.alpha_power_analysis(
        alpha_artifact,
        metadata.get_column("classification"),
        alpha=[0.05],
        power=[0.8]
    )


def test_beta_pa(beta_artifact, metadata):
    evident.methods.beta_power_analysis(
        beta_artifact,
        metadata.get_column("classification"),
        alpha=[0.05],
        power=[0.8]
    )


def test_alpha_effect_size_by_cat(alpha_artifact, metadata):
    non_pairwise = evident.methods.alpha_effect_size_by_category(
        alpha_diversity=alpha_artifact,
        sample_metadata=metadata,
        columns=["classification", "cd_behavior"]
    ).effect_size_results.view(pd.DataFrame)
    assert non_pairwise.shape == (2, 3)
    assert (non_pairwise.columns == ["effect_size", "metric", "column"]).all()

    pairwise = evident.methods.alpha_effect_size_by_category(
        alpha_diversity=alpha_artifact,
        sample_metadata=metadata,
        columns=["classification", "cd_behavior"],
        pairwise=True
    ).effect_size_results.view(pd.DataFrame)
    assert pairwise.shape == (4, 5)
    exp_cols = ["effect_size", "metric", "column", "group_1", "group_2"]
    assert (pairwise.columns == exp_cols).all()


def test_beta_effect_size_by_cat(beta_artifact, metadata):
    non_pairwise = evident.methods.beta_effect_size_by_category(
        beta_diversity=beta_artifact,
        sample_metadata=metadata,
        columns=["classification", "cd_behavior"]
    ).effect_size_results.view(pd.DataFrame)
    assert non_pairwise.shape == (2, 3)
    assert (non_pairwise.columns == ["effect_size", "metric", "column"]).all()

    pairwise = evident.methods.beta_effect_size_by_category(
        beta_diversity=beta_artifact,
        sample_metadata=metadata,
        columns=["classification", "cd_behavior"],
        pairwise=True
    ).effect_size_results.view(pd.DataFrame)
    assert pairwise.shape == (4, 5)
    exp_cols = ["effect_size", "metric", "column", "group_1", "group_2"]
    assert (pairwise.columns == exp_cols).all()


def test_alpha_effect_size_by_cat_parallel(alpha_artifact, metadata):
    non_pairwise = evident.methods.alpha_effect_size_by_category(
        alpha_diversity=alpha_artifact,
        sample_metadata=metadata,
        columns=["classification", "cd_behavior"],
        n_jobs=2
    ).effect_size_results.view(pd.DataFrame)
    assert non_pairwise.shape == (2, 3)
    assert (non_pairwise.columns == ["effect_size", "metric", "column"]).all()

    pairwise = evident.methods.alpha_effect_size_by_category(
        alpha_diversity=alpha_artifact,
        sample_metadata=metadata,
        columns=["classification", "cd_behavior"],
        pairwise=True,
        n_jobs=2
    ).effect_size_results.view(pd.DataFrame)
    assert pairwise.shape == (4, 5)
    exp_cols = ["effect_size", "metric", "column", "group_1", "group_2"]
    assert (pairwise.columns == exp_cols).all()


def test_beta_effect_size_by_cat_parallel(beta_artifact, metadata):
    non_pairwise = evident.methods.beta_effect_size_by_category(
        beta_diversity=beta_artifact,
        sample_metadata=metadata,
        columns=["classification", "cd_behavior"],
        n_jobs=2
    ).effect_size_results.view(pd.DataFrame)
    assert non_pairwise.shape == (2, 3)
    assert (non_pairwise.columns == ["effect_size", "metric", "column"]).all()

    pairwise = evident.methods.beta_effect_size_by_category(
        beta_diversity=beta_artifact,
        sample_metadata=metadata,
        columns=["classification", "cd_behavior"],
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
