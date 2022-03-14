import os
import glob

from bokeh.layouts import column, row
from bokeh.models import (ColumnDataSource, Select, NumericInput,
                          HoverTool)
from bokeh.plotting import curdoc, figure
import pandas as pd
from skbio import DistanceMatrix

from evident import AlphaDiversityHandler, BetaDiversityHandler

curr_path = os.path.dirname(__file__)
md_loc = os.path.join(curr_path, "data/metadata.tsv")
md = pd.read_table(md_loc, sep="\t", index_col=0)
cols = list(md.columns)
binary_cols = [
    col for col in cols if len(md[col].unique()) == 2
]
multiclass_cols = [col for col in cols if col not in binary_cols]

data_path = os.path.join(curr_path, "data")
data_loc = glob.glob(f"{data_path}/diversity*")[0]

if "alpha" in data_loc:
    alpha_div_data = pd.read_table(data_loc, sep="\t", index_col=0)
    dh = AlphaDiversityHandler(alpha_div_data, md)
elif "beta" in data_loc:
    beta_div_data = DistanceMatrix.read(data_loc)
    dh = BetaDiversityHandler(beta_div_data, md)
else:
    raise ValueError("No valid data found!")

kw = dict()
kw["x_range"] = [0, 110]
kw["y_range"] = [-0.1, 1.1]

# https://github.com/bokeh/bokeh/issues/2351#issuecomment-108101144
tools = ["pan", "reset", "box_zoom"]
hover = HoverTool(names=["points"])


# Much of this taken from
# https://github.com/bokeh/bokeh/tree/branch-3.0/examples/app/crossfilter
def create_figure():
    obs_range = range(min_obs.value, max_obs.value + 1, step_obs.value)

    plot = figure(height=600, width=600, tools=tools+[hover],
                  sizing_mode="stretch_width", **kw)
    plot.xaxis.axis_label = "Total Observations"
    plot.yaxis.axis_label = r"Power (1 - β)"

    for ax in [plot.xaxis, plot.yaxis]:
        ax.axis_label_text_font_size = "20px"

    res = dh.power_analysis(
        column=chosen_col.value,
        total_observations=obs_range,
        alpha=alpha.value
    ).to_dataframe()

    source = ColumnDataSource(res)
    plot.line(x="total_observations", y="power", source=source)
    plot.circle(x="total_observations", y="power", source=source,
                name="points", size=10)

    return plot


def update(attr, old, new):
    layout.children[1] = create_figure()


chosen_col = Select(options=cols, title="Column", value=cols[0])
alpha = NumericInput(low=0.00001, high=0.99999, value=0.05, mode="float",
                     title="Significance Level")
min_obs = NumericInput(low=10, value=10, mode="int",
                       title="Minimum Total Observations")
max_obs = NumericInput(value=100, mode="int",
                       title="Maximum Total Observations")
step_obs = NumericInput(low=0, high=max_obs.value, value=10,
                        mode="int", title="Observation Step Size")

controls = [chosen_col, alpha, min_obs, max_obs, step_obs]
for ctrl in controls:
    ctrl.on_change("value", update)

control_panel = column(*controls, width=200)
layout = row(control_panel, create_figure())

curdoc().add_root(layout)
curdoc().title = "Power Curve"
