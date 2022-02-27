import os
from shutil import copy
from typing import List

import matplotlib.pyplot as plt
import pandas as pd
from qiime2 import CategoricalMetadataColumn, Metadata
from skbio import DistanceMatrix

from evident import AlphaDiversityHandler, BetaDiversityHandler
from evident.exploration import (effect_size_by_category,
                                 pairwise_effect_size_by_category)
from evident.plotting import plot_power_curve as ppc

TBL_CSS = os.path.join(os.path.dirname(__file__), "dataframe.css")


def alpha_power_analysis(
    alpha_diversity: pd.Series,
    sample_metadata: CategoricalMetadataColumn,
    alpha: list = None,
    power: list = None,
    total_observations: list = None
) -> pd.DataFrame:
    res = _power_analysis(alpha_diversity, sample_metadata,
                          AlphaDiversityHandler, alpha=alpha, power=power,
                          total_observations=total_observations)
    return res


def beta_power_analysis(
    beta_diversity: DistanceMatrix,
    sample_metadata: CategoricalMetadataColumn,
    alpha: list = None,
    power: list = None,
    total_observations: list = None
) -> pd.DataFrame:
    res = _power_analysis(beta_diversity, sample_metadata,
                          BetaDiversityHandler, alpha=alpha, power=power,
                          total_observations=total_observations)
    return res


def _power_analysis(data, metadata, handler, **kwargs):
    md = metadata.to_series()
    column = md.name
    dh = handler(data, md.to_frame())
    res = dh.power_analysis(column, **kwargs)
    return res.to_dataframe()


def alpha_effect_size_by_category(
    alpha_diversity: pd.Series,
    sample_metadata: Metadata,
    columns: List[str],
    pairwise: bool = False
) -> pd.DataFrame:
    res = _effect_size_by_category(alpha_diversity, sample_metadata,
                                   AlphaDiversityHandler, columns, pairwise)
    return res


def beta_effect_size_by_category(
    beta_diversity: DistanceMatrix,
    sample_metadata: Metadata,
    columns: List[str],
    pairwise: bool = False
) -> pd.DataFrame:
    res = _effect_size_by_category(beta_diversity, sample_metadata,
                                   BetaDiversityHandler, columns, pairwise)
    return res


def _effect_size_by_category(data, metadata, handler, columns, pairwise):
    dh = handler(data, metadata.to_dataframe())
    if pairwise:
        df = pairwise_effect_size_by_category(dh, columns)
    else:
        df = effect_size_by_category(dh, columns)
    return df


def plot_power_curve(
    output_dir: str,
    power_analysis_results: pd.DataFrame,
    target_power: float = 0.8,
    style: str = "alpha"
) -> None:
    ppc(power_analysis_results, target_power, style, markers=True)
    plt.savefig(os.path.join(output_dir, "power_curve.svg"))
    index_fp = os.path.join(output_dir, "index.html")
    with open(index_fp, "w") as f:
        f.write("<html><body>\n")
        f.write("<img src='power_curve.svg' alt='Power curve'>")


def visualize_power_analysis_results(
    output_dir: str,
    power_analysis_results: pd.DataFrame,
) -> None:
    return


def visualize_effect_size_results(
    output_dir: str,
    effect_size_results: pd.DataFrame,
) -> None:
    index_fp = os.path.join(output_dir, "index.html")
    copy(TBL_CSS, output_dir)
    with open(index_fp, "w") as f:
        f.write("<html><body>\n")
        f.write("<link rel='stylesheet' href='dataframe.css'>")
        f.write("<font face='Arial'>\n")
        f.write(
            effect_size_results
            .reset_index(drop=True)
            .to_html(index_names=False, index=False)
        )
        f.write("</font>")
