import os
from shutil import copy

import matplotlib.pyplot as plt
import pandas as pd

from evident.plotting import plot_power_curve as ppc

PATH_LOC = os.path.dirname(__file__)
CURVE_CSS = os.path.join(PATH_LOC, "curve.css")
TBL_CSS = os.path.join(PATH_LOC, "dataframe.css")


def plot_power_curve(
    output_dir: str,
    power_analysis_results: pd.DataFrame,
    target_power: float = 0.8,
    style: str = "alpha"
) -> None:
    index_fp = os.path.join(output_dir, "index.html")
    copy(CURVE_CSS, output_dir)
    ppc(power_analysis_results, target_power, style, markers=True)

    fig_loc = os.path.join(output_dir, "power_curve.svg")
    fig_loc2 = os.path.join(output_dir, "power_curve.pdf")
    plt.savefig(fig_loc)
    plt.savefig(fig_loc2)

    results_loc = os.path.join(output_dir, "results.tsv")
    power_analysis_results.to_csv(results_loc, sep="\t", index=False)

    with open(index_fp, "w") as f:
        f.write("<html><body>\n")
        f.write("<font face='Arial'>\n")
        f.write(
            "<div style='text-align: center;'>\n"
            "<a href='power_curve.pdf' target='_blank'"
            "rel='noopener noreferrer'>"
            "Download plot as PDF</a><br>\n"
            "<a href='results.tsv'>Download results as TSV</a><br>\n"
        )
        f.write("<img src='power_curve.svg' alt='Power curve'>\n")
        f.write("</div>\n")
        f.write("</font>")


def visualize_results(
    output_dir: str,
    results: pd.DataFrame,
) -> None:
    index_fp = os.path.join(output_dir, "index.html")
    copy(TBL_CSS, output_dir)
    results_loc = os.path.join(output_dir, "results.tsv")
    results.to_csv(results_loc, sep="\t", index=False)

    with open(index_fp, "w") as f:
        f.write("<html><body>\n")
        f.write("<link rel='stylesheet' href='dataframe.css'>")
        f.write("<font face='Arial'>\n")
        f.write("<a href='results.tsv'>Download table as TSV</a>\n")
        f.write(
            results
            .reset_index(drop=True)
            .dropna(axis=1, how="all")
            .to_html(index_names=False, index=False)
        )
        f.write("</font>")
