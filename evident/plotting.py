import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def plot_power_curve(
    power_df: pd.DataFrame,
    target_power: float = 0.8,
    style: str = "alpha",
    **kwargs
):
    fig, ax = plt.subplots(1, 1)
    sns.lineplot(
        data=power_df,
        x="total_observations",
        y="power",
        markers=True,
        **kwargs
    )
    ax.hline(target_power, zorder=0)
    ax.grid(linewidth=0.2)
    ax.set_axisbelow(True)
    ax.set_ylabel(r"Power (1 - $\beta$)", fontsize="large")
    ax.set_xlabel("Total Observations", fontsize="large")
    return ax
