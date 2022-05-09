import os
import glob

from bokeh.layouts import column, row
from bokeh.models import (ColumnDataSource, Select, NumericInput, HoverTool,
                          MultiChoice, CheckboxGroup)
from bokeh.models.widgets import Tabs, Panel
from bokeh.plotting import curdoc, figure
from bokeh.transform import jitter
import pandas as pd
import seaborn as sns
from skbio import DistanceMatrix

from evident import UnivariateDataHandler, MultivariateDataHandler
from evident.effect_size import effect_size_by_category

curr_path = os.path.dirname(__file__)
md_loc = os.path.join(curr_path, "data/metadata.tsv")
md = pd.read_table(md_loc, sep="\t", index_col=0)
cols = list(md.columns)

binary_cols = [
    col for col in cols if len(md[col].dropna().unique()) == 2
]
multiclass_cols = [col for col in cols if col not in binary_cols]

data_path = os.path.join(curr_path, "data")
data_loc = glob.glob(f"{data_path}/data*")[0]

if "univariate" in data_loc:
    univariate_data = pd.read_table(data_loc, sep="\t", index_col=0)
    # Loads as DataFrame. Need to squeeze to Series for UDH.
    dh = UnivariateDataHandler(univariate_data.squeeze(), md)
    data_type = "Univariate"
    data_name = univariate_data.squeeze().name
elif "multivariate" in data_loc:
    multivariate_data = DistanceMatrix.read(data_loc)
    dh = MultivariateDataHandler(multivariate_data, md)
    data_type = "Multivariate"
    data_name = "Within-Group Distances"
else:
    raise ValueError("No valid data found!")

blues = sns.color_palette("Blues", len(binary_cols)).as_hex()
reds = sns.color_palette("Reds", len(multiclass_cols)).as_hex()

binary_effect_sizes = (
    effect_size_by_category(dh, binary_cols)
    .to_dataframe()
    .assign(color=blues[::-1])
)
mc_effect_sizes = (
    effect_size_by_category(dh, multiclass_cols)
    .to_dataframe()
    .assign(color=reds[::-1])
)
color_dict = dict(zip(
    binary_effect_sizes["column"],
    binary_effect_sizes["color"]
))
color_dict.update(dict(zip(
    mc_effect_sizes["column"],
    mc_effect_sizes["color"]
)))

chosen_box_col = Select(options=cols, title="Boxplot Column", value=cols[0])
show_points_check = CheckboxGroup(
    labels=["Show scatter points"],
    active=[],
)
show_points = False

col_select = MultiChoice(options=cols, value=[cols[0]],
                         title="Power Curve Columns")
alpha = NumericInput(low=0.00001, high=0.99999, value=0.05, mode="float",
                     title="Significance Level")
min_obs = NumericInput(low=10, value=10, mode="int",
                       title="Minimum Total Observations")
max_obs = NumericInput(value=100, mode="int",
                       title="Maximum Total Observations")
step_obs = NumericInput(low=0, high=max_obs.value, value=10,
                        mode="int", title="Observation Step Size")

summary_controls = [alpha, min_obs, max_obs, step_obs, col_select]
box_controls = [chosen_box_col, show_points_check]

metric_dict = {"cohens_f": "Cohen's f", "cohens_d": "Cohen's d"}


def get_barplots():
    """Get static barplots of Cohen's d & f."""
    def create_barplot(df, title):
        metric = metric_dict[df["metric"].unique().item()]
        hover = HoverTool()
        hover.tooltips = [
            ("Column", "@column"),
            (metric, "@effect_size{0.000}")
        ]
        tools = [hover, "pan", "reset", "box_zoom", "save"]

        source = ColumnDataSource(df)
        p = figure(y_range=df["column"][::-1], title=title,
                   tools=tools, sizing_mode="stretch_both")
        p.hbar(y="column", right="effect_size", height=0.9, source=source,
               color="color")
        p.y_range.range_padding = 0.1
        p.xaxis.axis_label = metric
        p.ygrid.grid_line_color = None

        for ax in [p.xaxis, p.yaxis]:
            ax.axis_label_text_font_size = "15pt"
            ax.axis_label_text_font_style = "normal"
            ax.major_tick_line_width = 0
        p.yaxis.major_label_text_font_size = "10pt"

        return p

    bin_bars = create_barplot(binary_effect_sizes, "Binary Categories")
    mc_bars = create_barplot(mc_effect_sizes, "Multi-Class Categories")

    return bin_bars, mc_bars


def get_curves():
    """Get reactive power curves."""
    kw = dict()
    kw["x_range"] = [0, 110]
    kw["y_range"] = [-0.1, 1.1]

    # https://github.com/bokeh/bokeh/issues/2351#issuecomment-108101144
    tools = ["pan", "reset", "box_zoom", "save"]
    hover = HoverTool(names=["points"])
    hover.tooltips = [
        ("Column", "@column"),
        ("Metric", "@metric"),
        ("Effect Size", "@effect_size{0.000}"),
        ("Total Observations", "@total_observations"),
        ("Power", "@power{0.000}"),
    ]

    # Much of this taken from
    # https://github.com/bokeh/bokeh/tree/branch-3.0/examples/app/crossfilter
    kw["x_range"][-1] = max_obs.value + step_obs.value  # Resize x-axis
    obs_range = range(
        min_obs.value,
        max_obs.value + 1,
        step_obs.value
    )

    curve = figure(tools=tools+[hover], **kw,
                   sizing_mode="stretch_both")
    curve.title.text = "Power Curve"
    curve.xaxis.axis_label = "Total Observations"
    curve.yaxis.axis_label = r"Power (1 - β)"

    for ax in [curve.xaxis, curve.yaxis]:
        ax.axis_label_text_font_size = "15pt"
        ax.major_label_text_font_size = "10pt"
        ax.axis_label_text_font_style = "normal"

    for col in col_select.value:
        res = dh.power_analysis(
            column=col,
            total_observations=obs_range,
            alpha=alpha.value
        ).to_dataframe()
        res["metric"] = res["metric"].map(metric_dict)

        source = ColumnDataSource(res)
        curve_args = {"x": "total_observations", "y": "power",
                      "source": source}
        curve.line(**curve_args, line_color=color_dict[col])
        curve.circle(**curve_args, color=color_dict[col], name="points",
                     size=10)

    return curve


def get_boxplot(show_points):
    groups = sorted(md[chosen_box_col.value].dropna().unique())
    es_res = dh.calculate_effect_size(chosen_box_col.value)
    effect_size = es_res.effect_size
    metric = metric_dict[es_res.metric]

    group_vals = []
    groups_with_n = []
    rename_dict = dict()
    for i, grp in enumerate(groups):
        grp_idx = md[md[chosen_box_col.value] == grp].index
        vals = dh.subset_values(grp_idx)
        n = len(vals)
        groups_with_n.append(f"{grp} (n = {n})")
        rename_dict[grp] = f"{grp} (n = {n})"
        vals = pd.DataFrame.from_dict(
            {"group": grp, "value": vals, "n": n}
        )
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
    out = gb.apply(outliers).dropna()["value"]

    if not out.empty:
        outx = [rename_dict[x] for x in out.index.get_level_values(0)]
        outy = list(out.values)

    qmin = gb.quantile(q=0.00)
    qmax = gb.quantile(q=1.00)
    uv = upper.value
    lv = lower.value
    upper.value = [
        min([x, y]) for (x, y) in zip(list(qmax.loc[:, "value"]), uv)
    ]
    lower.value = [
        max([x, y]) for (x, y) in zip(list(qmin.loc[:, "value"]), lv)
    ]

    lw = 2
    pal = sns.color_palette("colorblind", len(groups)).as_hex()

    boxes = figure(tools=["reset", "save", "box_zoom", "pan"],
                   y_range=groups_with_n, sizing_mode="stretch_width")

    box_args = {"y": groups_with_n, "height": 0.7, "line_color": "black",
                "fill_color": pal, "line_width": lw}
    boxes.hbar(**box_args, left=q1.value, right=q2.value)
    boxes.hbar(**box_args, left=q2.value, right=q3.value)

    seg_args = {"y0": groups_with_n, "y1": groups_with_n,
                "line_color": "black", "line_width": lw}
    boxes.segment(**seg_args, x0=upper.value, x1=q3.value)
    boxes.segment(**seg_args, x0=lower.value, x1=q1.value)

    whisker_args = {"y": groups_with_n, "height": 0.2, "width": 0.00001,
                    "line_color": "black", "line_width": lw}
    boxes.rect(**whisker_args, x=lower.value)
    boxes.rect(**whisker_args, x=upper.value)

    if not out.empty:
        boxes.diamond(y=outx, x=outy, size=15, color="white",
                      line_color="black")

    boxes.ygrid.grid_line_color = None
    boxes.xaxis.axis_label = data_name
    boxes.title.text = (
        f"{data_type} Data - {chosen_box_col.value}\n"
        f"{metric} = {effect_size:.3f}"
    )
    boxes.title.text_font_size = "10pt"

    for ax in [boxes.xaxis, boxes.yaxis]:
        ax.axis_label_text_font_size = "15pt"
        ax.axis_label_text_font_style = "normal"
        ax.major_tick_line_width = 0
    boxes.yaxis.major_label_text_font_size = "12pt"

    group_df["group"] = group_df["group"].map(rename_dict)
    if show_points:
        boxes.circle(y=jitter("group", 0.4, range=boxes.y_range), x="value",
                     source=ColumnDataSource(group_df), color="black",
                     size=5)

    return boxes


def update_plots(attr, old, new):
    # Set show points to False when column changes
    curve = get_curves()
    plots.children[1] = curve


def update_boxplot(attr, old, new):
    show_points_check.active = []
    show_points = False
    boxes = get_boxplot(show_points)
    page2.children[1] = boxes


def toggle_box_points(attr, old, new):
    # Empty list is falsy
    show_points = bool(show_points_check.active)
    boxes = get_boxplot(show_points)
    page2.children[1] = boxes


for ctrl in summary_controls:
    ctrl.on_change("value", update_plots)

chosen_box_col.on_change("value", update_boxplot)
show_points_check.on_change("active", toggle_box_points)

summary_control_panel = column(*summary_controls, width=200)
curve = get_curves()
barplot_col = column(*get_barplots())
plots = row(barplot_col, curve)
page1 = row(summary_control_panel, plots, sizing_mode="stretch_height")
panel1 = Panel(child=page1, title="Summary")

box_control_panel = column(*box_controls, width=200)
page2 = row(box_control_panel, get_boxplot(show_points))
panel2 = Panel(child=page2, title="Data")

tabs = Tabs(tabs=[panel1, panel2])

curdoc().add_root(tabs)
curdoc().title = "Evident"
