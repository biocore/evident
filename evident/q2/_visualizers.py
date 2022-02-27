import os
from shutil import copy

import matplotlib.pyplot as plt
import pandas as pd

from evident.plotting import plot_power_curve as ppc


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


def visualize_results(
    output_dir: str,
    results: pd.DataFrame,
) -> None:
    index_fp = os.path.join(output_dir, "index.html")
    copy(TBL_CSS, output_dir)
    with open(index_fp, "w") as f:
        f.write("<html><body>\n")
        f.write("<link rel='stylesheet' href='dataframe.css'>")
        f.write("<font face='Arial'>\n")
        f.write(
            results
            .reset_index(drop=True)
            .dropna(axis=1, how="all")
            .to_html(index_names=False, index=False)
        )
        f.write("</font>")
