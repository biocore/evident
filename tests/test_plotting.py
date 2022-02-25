import os

import pandas as pd

from evident.diversity_handler import AlphaDiversityHandler
from evident.plotting import plot_power_curve


def test_plot_power_curve():
    fname = os.path.join(os.path.dirname(__file__), "data/metadata.tsv")
    df = pd.read_table(fname, sep="\t", index_col=0)
    a = AlphaDiversityHandler(df["faith_pd"], df)

    alpha = [0.01, 0.05, 0.1]
    res = a.power_analysis(column="classification", alpha=alpha, power=0.8)
    plot_power_curve(res)
