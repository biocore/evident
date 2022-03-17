import os
import glob

from bokeh.layouts import column, row
from bokeh.models import (ColumnDataSource, Select, NumericInput, HoverTool,
                          Legend, LegendItem)
from bokeh.plotting import curdoc, figure
import pandas as pd
import seaborn as sns
from skbio import DistanceMatrix

from evident import AlphaDiversityHandler, BetaDiversityHandler

curr_path = os.path.dirname(__file__)
md_loc = os.path.join(curr_path, "data/metadata.tsv")
md = pd.read_table(md_loc, sep="\t", index_col=0)
cols = list(md.columns)
binary_cols = [
    col for col in cols if len(md[col].dropna().unique()) == 2
]
multiclass_cols = [col for col in cols if col not in binary_cols]

data_path = os.path.join(curr_path, "data")
data_loc = glob.glob(f"{data_path}/diversity*")[0]

if "alpha" in data_loc:
    alpha_div_data = pd.read_table(data_loc, sep="\t", index_col=0)
    # Loads as DataFrame. Need to squeeze to Series for ADH.
    dh = AlphaDiversityHandler(alpha_div_data.squeeze(), md)
    div_type = "Alpha"
    ylabel = "Alpha Diversity"
elif "beta" in data_loc:
    beta_div_data = DistanceMatrix.read(data_loc)
    dh = BetaDiversityHandler(beta_div_data, md)
    div_type = "Beta"
    ylabel = "Within-Group Distances"
else:
    raise ValueError("No valid data found!")

kw = dict()
kw["x_range"] = [0, 110]
kw["y_range"] = [-0.1, 1.1]

plots_kw = {
    "width": 600,
    "height": 600,
    "sizing_mode": "scale_both",
}

# https://github.com/bokeh/bokeh/issues/2351#issuecomment-108101144
tools = ["pan", "reset", "box_zoom", "save"]
hover = HoverTool(names=["points"])


# Much of this taken from
# https://github.com/bokeh/bokeh/tree/branch-3.0/examples/app/crossfilter
def create_figure():
    kw["x_range"][-1] = max_obs.value + step_obs.value  # Resize x-axis
    obs_range = range(
        min_obs.value,
        max_obs.value + 1,
        step_obs.value
    )

    curve = figure(tools=tools+[hover], **kw, **plots_kw)
    curve.xaxis.axis_label = "Total Observations"
    curve.yaxis.axis_label = r"Power (1 - β)"

    for ax in [curve.xaxis, curve.yaxis]:
        ax.axis_label_text_font_size = "15pt"
        ax.major_label_text_font_size = "10pt"
        ax.axis_label_text_font_style = "normal"

    groups = sorted(md[chosen_col.value].dropna().unique())
    if len(groups) == 2:
        metric = "Cohen's d"
    else:
        metric = "Cohen's f"

    res = dh.power_analysis(
        column=chosen_col.value,
        total_observations=obs_range,
        alpha=alpha.value
    ).to_dataframe()
    effect_size = res["effect_size"].unique().item()

    curve.title.text = (
        f"{div_type} Diversity - {chosen_col.value}\n"
        f"{metric} = {effect_size:.3f}"
    )
    curve.title.text_font_size = "10pt"

    source = ColumnDataSource(res)
    curve_args = {"x": "total_observations", "y": "power", "source": source,
                  "color": "black"}
    curve.line(**curve_args)
    curve.circle(**curve_args, name="points", size=10)

    # Boxplots
    # https://docs.bokeh.org/en/latest/docs/gallery/boxplot.html

    group_vals = []
    groups_with_n = []
    for i, grp in enumerate(groups):
        grp_idx = md[md[chosen_col.value] == grp].index
        vals = dh.subset_values(grp_idx)
        n = len(vals)
        groups_with_n.append(f"{grp} (n = {n})")
        vals = pd.DataFrame.from_dict({"group": grp, "value": vals, "n": n})
        group_vals.append(vals)
    group_df = pd.concat(group_vals)

    gb = group_df.groupby("group")
    q1 = gb.quantile(q=0.25)
    q2 = gb.quantile(q=0.5)
    q3 = gb.quantile(q=0.75)
    iqr = q3 - q1
    upper = q3 + 1.5*iqr
    lower = q1 - 1.5*iqr

    def outliers(grp):
        cat = grp.name
        low = grp.value > upper.loc[cat]["value"]
        high = grp.value < lower.loc[cat]["value"]
        res = grp[low | high]
        return res
    out = gb.apply(outliers).dropna()

    if not out.empty:
        outx = list(out.index.get_level_values(0))
        outy = list(out.values)

    qmin = gb.quantile(q=0.00)
    qmax = gb.quantile(q=1.00)
    upper.value = [
        min([x, y]) for (x, y) in zip(list(qmax.loc[:, "value"]), upper.value)
    ]
    lower.value = [
        max([x, y]) for (x, y) in zip(list(qmin.loc[:, "value"]), lower.value)
    ]

    lw = 2
    pal = sns.color_palette("colorblind", len(groups)).as_hex()

    boxes = figure(tools=[hover, "reset", "save"], x_range=groups_with_n,
                   **plots_kw)

    box_args = {"x": groups_with_n, "width": 0.7, "line_color": "black",
                "fill_color": pal, "line_width": lw}
    box = boxes.vbar(**box_args, bottom=q1.value, top=q2.value)
    boxes.vbar(**box_args, bottom=q2.value, top=q3.value)

    # https://tinyurl.com/bp7axw9v
    legend = Legend(
        items=[LegendItem(label=dict(field="x"), renderers=[box])],
        location="top",
        border_line_width=1,
        border_line_color="black"
    )
    boxes.add_layout(legend, "right")
    boxes.xaxis.major_label_text_font_size = "0pt"

    seg_args = {"x0": groups_with_n, "x1": groups_with_n,
                "line_color": "black", "line_width": lw}
    boxes.segment(**seg_args, y0=upper.value, y1=q3.value)
    boxes.segment(**seg_args, y0=lower.value, y1=q1.value)

    whisker_args = {"x": groups_with_n, "width": 0.2, "height": 0.00001,
                    "line_color": "black", "line_width": lw}
    boxes.rect(**whisker_args, y=lower.value)
    boxes.rect(**whisker_args, y=upper.value)

    if not out.empty:
        boxes.circle(outx, outy, size=6, color="black", fill_alpha=0.6)

    boxes.xaxis.major_label_text_font_size = "0pt"
    boxes.xaxis.axis_label = chosen_col.value
    boxes.xgrid.grid_line_color = None
    boxes.yaxis.axis_label = ylabel
    boxes.title.text = (
        f"{div_type} Diversity - {chosen_col.value}\n"
        f"{metric} = {effect_size:.3f}"
    )
    boxes.title.text_font_size = "10pt"

    for ax in [boxes.xaxis, boxes.yaxis]:
        ax.axis_label_text_font_size = "15pt"
        ax.axis_label_text_font_style = "normal"
        ax.major_tick_line_width = 0
    boxes.yaxis.major_label_text_font_size = "10pt"

    return curve, boxes


def update(attr, old, new):
    curve, boxes = create_figure()
    plots.children[0] = curve
    plots.children[1] = boxes


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

control_panel = column(
    *controls,
    width=200,
    height=200,
)
plots = row(*create_figure(), **plots_kw)
layout = row(
    control_panel,
    plots,
)

curdoc().add_root(layout)
curdoc().title = "Evident"
