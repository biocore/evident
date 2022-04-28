from typing import Union

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from evident.results import PowerAnalysisResults


def plot_power_curve(
    results: Union[PowerAnalysisResults, pd.DataFrame],
    target_power: float = 0.8,
    style: str = "alpha",
    **kwargs
):
    """Plot power curve from multiple power analyses.

    x-axis is total_observations and y-axis is power

    :param results: Results from power analyses
    :type results: evident.power.PowerAnalysisResults

    :param target_power: Where to draw line denoting target power, defaults to
        0.8
    :type target_power: float

    :param style: Value to use as style, must be one of 'alpha' (default),
        'effect_size', or 'difference'
    :type style: str

    :param kwargs: Any additional arguments to pass into sns.lineplot
    """
    if isinstance(results, PowerAnalysisResults):
        power_df = results.to_dataframe()
    else:
        power_df = results

    fig, ax = plt.subplots(1, 1, dpi=300, facecolor="white")
    sns.lineplot(
        data=power_df,
        x="total_observations",
        y="power",
        style=style,
        **kwargs
    )
    ax.axhline(target_power, zorder=0, color="black")
    ax.grid(linewidth=0.2)
    ax.set_axisbelow(True)
    ax.set_ylabel(r"Power (1 - $\beta$)", fontsize="large")
    ax.set_xlabel("Total Observations", fontsize="large")
    return ax
