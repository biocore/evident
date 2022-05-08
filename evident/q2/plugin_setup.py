import importlib

from qiime2.plugin import (Plugin, Int, Float, List, Range, Choices, Str,
                           Citations, Bool, Metadata)
from q2_types.sample_data import SampleData, AlphaDiversity
from q2_types.distance_matrix import DistanceMatrix

from evident import __version__
from ._format import PowerAnalysisResultsDirectoryFormat as PARsDirFmt
from ._format import EffectSizeResultsDirectoryFormat as ERsDirFmt
from ._type import PowerAnalysisResults, EffectSizeResults
from ._methods import (univariate_power_analysis, bivariate_power_analysis,
                       univariate_effect_size_by_category,
                       bivariate_effect_size_by_category,
                       univariate_power_analysis_repeated_measures)
from ._visualizers import plot_power_curve, visualize_results


Probability = Float % Range(0, 1, inclusive_end=False)
Correlation = Float % Range(-1, 1, inclusive_end=True)

PA_PARAM_DESCS = {
    "group_column": "Column to use for groupings.",
    "sample_metadata": "Sample metadata.",
    "alpha": "Significance level.",
    "power": (
        "Probability of rejecting the null hypothesis given that the "
        "alternative is true."
    ),
    "total_observations": (
        "Total number of observations to consider. Groups are assumed to "
        "be all the same size."
    ),
    "difference": (
        "Difference between groups to consider. If this argument is provided, "
        "evident will use this value instead of calculating the mean "
        "difference. The pooled standard deviation of the groups will still "
        "be used. If not provided, evident will calculate the difference in "
        "means automatically."
    ),
    "max_levels_per_category": (
        "Max number of levels in a category to keep. Any categorical columns "
        "that have more than this number of unique levels will not be saved, "
        "defaults to 5."
    ),
    "min_count_per_level": (
        "Min number of samples in a given category level to keep. Any levels "
        "that have fewer than this many samples will not be saved, defaults "
        "to 3."
    )
}

ES_PARAM_DESCS = {
    "sample_metadata": "Sample metadata.",
    "group_columns": "List of columns for which to calculate effect size.",
    "pairwise": (
        "Whether to calculate pairwise effect sizes within groups "
        "with more than 2 levels. If true, computes Cohen's d for all "
        "pairwise comparisons. If false (default), computes Cohen's f "
        "for each group overall."
    ),
    "n_jobs": (
        "Number of jobs to run in parallel, defaults to no parallelization."
    ),
    "max_levels_per_category": (
        "Max number of levels in a category to keep. Any categorical columns "
        "that have more than this number of unique levels will not be saved, "
        "defaults to 5."
    ),
    "min_count_per_level": (
        "Min number of samples in a given category level to keep. Any levels "
        "that have fewer than this many samples will not be saved, defaults "
        "to 3."
    )
}

citations = Citations.load("citations.bib", package="evident")

plugin = Plugin(
    name="evident",
    version=__version__,
    website="https://github.com/biocore/evident",
    citations=[citations["Casals-Pascual2020"]],
    short_description="Plugin for effect size calculations",
    description=(
        "Perform power analysis on microbiome data. Supports "
        "calculation of effect size given metadata covariates and supporting "
        "visualizations."
    ),
    package="evident"
)


UNIV_PA_PARAM_DESCS = PA_PARAM_DESCS.copy()
UNIV_PA_PARAM_DESCS["data_column"] = "Column in metadata containing data."

# QIIME 2 needs an input so we provide SampleData[AlphaDiversity] which is
# optional. Can't provide just SampleData, unfortunately.
plugin.methods.register_function(
    function=univariate_power_analysis,
    inputs={"data": SampleData[AlphaDiversity]},
    input_descriptions={"data": "Sample data"},
    parameters={
        "group_column": Str,
        "data_column": Str,
        "sample_metadata": Metadata,
        "alpha": List[Probability],
        "power": List[Probability],
        "total_observations": List[Int],
        "difference": List[Float],
        "max_levels_per_category": Int,
        "min_count_per_level": Int
    },
    parameter_descriptions=UNIV_PA_PARAM_DESCS,
    outputs=[("power_analysis_results", PowerAnalysisResults)],
    name="Univariate data power analysis.",
    description=(
        "Use sample univariate data to perform power calculations "
        "for desired significance level, power, or sample size. Exactly one "
        "of alpha, power, or sample size must be excluded."
    )
)

plugin.methods.register_function(
    function=bivariate_power_analysis,
    inputs={
        "data": DistanceMatrix,
    },
    input_descriptions={
        "data": "Sample distance matrix",
    },
    parameters={
        "group_column": Str,
        "sample_metadata": Metadata,
        "alpha": List[Probability],
        "power": List[Probability],
        "total_observations": List[Int],
        "difference": List[Float],
        "max_levels_per_category": Int,
        "min_count_per_level": Int
    },
    parameter_descriptions=PA_PARAM_DESCS,
    outputs=[("power_analysis_results", PowerAnalysisResults)],
    name="Bivariate data power analysis.",
    description=(
        "Use sample Bivariate data data to perform power calculations "
        "for desired significance level, power, or sample size."
    )
)

rm_param_descs = {
    k: v for k, v in PA_PARAM_DESCS.items()
    if k not in ["total_observations", "difference", "power",
                 "group_column"]
}
rm_param_descs["individual_id_column"] = (
    "Metadata column containing IDs for individual subjects."
)
rm_param_descs["state_column"] = (
    "Metadata column containing state (time) variable information."
)
rm_param_descs["subjects"] = "Number of subjects."
rm_param_descs["measurements"] = "Number of measurements per subject."
rm_param_descs["correlation"] = "Correlation between repeated measurements."
rm_param_descs["epsilon"] = "Sphericity parameter."
rm_param_descs["data_column"] = "Column in metadata containing data."

plugin.methods.register_function(
    function=univariate_power_analysis_repeated_measures,
    inputs={"data": SampleData[AlphaDiversity]},
    input_descriptions={"data": "Univariate data vector"},
    parameters={
        "sample_metadata": Metadata,
        "individual_id_column": Str,
        "data_column": Str,
        "state_column": Str,
        "subjects": List[Int],
        "measurements": List[Int],
        "alpha": List[Probability],
        "correlation": List[Correlation],
        "epsilon": List[Probability],
        "max_levels_per_category": Int,
        "min_count_per_level": Int
    },
    parameter_descriptions=rm_param_descs,
    outputs=[("power_analysis_results", PowerAnalysisResults)],
    name="Univariate data power analysis for repeated measures.",
    description=(
        "Use sample univariate data to perform power calculations "
        "for repeated measures."
    )
)

plugin.methods.register_function(
    function=univariate_effect_size_by_category,
    inputs={"data": SampleData[AlphaDiversity]},
    input_descriptions={"data": "Univariate data vector"},
    parameters={
        "sample_metadata": Metadata,
        "data_column": Str,
        "group_columns": List[Str],
        "pairwise": Bool,
        "n_jobs": Int,
        "max_levels_per_category": Int,
        "min_count_per_level": Int
    },
    parameter_descriptions=ES_PARAM_DESCS,
    outputs=[("effect_size_results", EffectSizeResults)],
    name="Univariate data effect size by category.",
    description=(
        "Calculate univariate data difference effect size of multiple "
        "categories."
    )
)

plugin.methods.register_function(
    function=bivariate_effect_size_by_category,
    inputs={"data": DistanceMatrix},
    input_descriptions={"data": "Bivariate data distance matrix"},
    parameters={
        "sample_metadata": Metadata,
        "group_columns": List[Str],
        "pairwise": Bool,
        "n_jobs": Int,
        "max_levels_per_category": Int,
        "min_count_per_level": Int
    },
    parameter_descriptions=ES_PARAM_DESCS,
    outputs=[("effect_size_results", EffectSizeResults)],
    name="Bivariate data effect size by category.",
    description=(
        "Calculate bivariate data difference effect size of multiple "
        "categories."
    )
)

plugin.visualizers.register_function(
    function=plot_power_curve,
    inputs={"power_analysis_results": PowerAnalysisResults},
    input_descriptions={
        "power_analysis_results": "Results from power analysis calculations"
    },
    parameters={
        "target_power": Probability,
        "style": Str % Choices({"alpha", "effect_size", "difference"})
    },
    parameter_descriptions={
        "target_power": "Value at which to draw horizontal power line.",
        "style": "Whether to use 'alpha', 'effect_size', or 'difference' "
        "as style."
    },
    name="Plot power curve.",
    description=(
        "Plot power curve based on power analysis results. x-axis is total "
        "number of observations and y-axis is power."
    )
)

plugin.visualizers.register_function(
    function=visualize_results,
    inputs={
        "results": PowerAnalysisResults | EffectSizeResults,
    },
    parameters={},
    input_descriptions={
        "results": "Either power analysis or effect size results."
    },
    name="Tabulate evident results.",
    description=(
        "Create a tabular visualization of either power analysis or effect "
        "size results."
    )
)

plugin.register_semantic_types(PowerAnalysisResults)
plugin.register_semantic_type_to_format(
    PowerAnalysisResults,
    artifact_format=PARsDirFmt
)
plugin.register_formats(PARsDirFmt)

plugin.register_semantic_types(EffectSizeResults)
plugin.register_semantic_type_to_format(
    EffectSizeResults,
    artifact_format=ERsDirFmt
)
plugin.register_formats(ERsDirFmt)

importlib.import_module("evident.q2._transformer")
