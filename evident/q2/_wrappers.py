import os

import matplotlib.pyplot as plt
import pandas as pd
from qiime2 import CategoricalMetadataColumn
from skbio import DistanceMatrix

from evident import AlphaDiversityHandler, BetaDiversityHandler
from evident.plotting import plot_power_curve as ppc


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
