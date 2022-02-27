import importlib

from qiime2.plugin import (Plugin, MetadataColumn, Categorical, Int, Float,
                           List, Range, Choices, Str, Citations, Bool,
                           Metadata)
from q2_types.sample_data import SampleData, AlphaDiversity
from q2_types.distance_matrix import DistanceMatrix

from evident import __version__
from ._format import PowerAnalysisResultsDirectoryFormat as PARsDirFmt
from ._format import EffectSizeResultsDirectoryFormat as ERsDirFmt
from ._type import PowerAnalysisResults, EffectSizeResults
from ._wrappers import (alpha_power_analysis, beta_power_analysis,
                        plot_power_curve, alpha_effect_size_by_category,
                        beta_effect_size_by_category)


Probability = Float % Range(0, 1, inclusive_end=False)

PA_PARAM_DESCS = {
    "sample_metadata": "Categorical sample metadata column.",
    "alpha": "Significance level",
    "power": (
        "Probability of rejecting the null hypothesis given that the "
        "alternative is true."
    ),
    "total_observations": (
        "Total number of observations to consider. Groups are assumed to "
        "be all the same size."
    )
}

ES_PARAM_DESCS = {
    "sample_metadata": "Sample metadata.",
    "columns": "List of columns for which to calculate effect size.",
    "pairwise": (
        "Whether to calculate pairwise effect sizes within groups "
        "with more than 2 levels. If true, computes Cohen's d for all "
        "pairwise comparisons. If false (default), computes Cohen's f "
        "for each group overall."
    )
}

citations = Citations.load("citations.bib", package="evident")

plugin = Plugin(
    name="evident",
    version=__version__,
    website="https://github.com/gibsramen/evident",
    citations=[citations["Casals-Pascual2020"]],
    short_description="Plugin for diversity effect size calculations",
    description=(
        "Perform power analysis on microbiome diversity data. Supports "
        "calculation of effect size given metadata covariates and supporting "
        "visualizations."
    ),
    package="evident"
)


plugin.methods.register_function(
    function=alpha_power_analysis,
    inputs={
        "alpha_diversity": SampleData[AlphaDiversity],
    },
    input_descriptions={"alpha_diversity": "Alpha diversity vector"},
    parameters={
        "sample_metadata": MetadataColumn[Categorical],
        "alpha": List[Probability],
        "power": List[Probability],
        "total_observations": List[Int]
    },
    parameter_descriptions=PA_PARAM_DESCS,
    outputs=[("power_analysis_results", PowerAnalysisResults)],
    name="Alpha diversity power analysis.",
    description=(
        "Use sample alpha diversity data to perform power calculations "
        "for desired significance level, power, or sample size."
    )
)

plugin.methods.register_function(
    function=beta_power_analysis,
    inputs={
        "beta_diversity": DistanceMatrix,
    },
    input_descriptions={"beta_diversity": "Beta diversity distance matrix"},
    parameters={
        "sample_metadata": MetadataColumn[Categorical],
        "alpha": List[Probability],
        "power": List[Probability],
        "total_observations": List[Int]
    },
    parameter_descriptions=PA_PARAM_DESCS,
    outputs=[("power_analysis_results", PowerAnalysisResults)],
    name="Beta diversity power analysis.",
    description=(
        "Use sample beta diversity data to perform power calculations "
        "for desired significance level, power, or sample size."
    )
)

plugin.methods.register_function(
    function=alpha_effect_size_by_category,
    inputs={
        "alpha_diversity": SampleData[AlphaDiversity],
    },
    input_descriptions={"alpha_diversity": "Alpha diversity vector"},
    parameters={
        "sample_metadata": Metadata,
        "columns": List[Str],
        "pairwise": Bool
    },
    parameter_descriptions=ES_PARAM_DESCS,
    outputs=[("effect_size_results", EffectSizeResults)],
    name="Alpha diversity effect size by category.",
    description=(
        "brehhhh"
    )
)

plugin.methods.register_function(
    function=beta_effect_size_by_category,
    inputs={
        "beta_diversity": DistanceMatrix,
    },
    input_descriptions={"beta_diversity": "Beta diversity distance matrix"},
    parameters={
        "sample_metadata": Metadata,
        "columns": List[Str],
        "pairwise": Bool
    },
    parameter_descriptions=ES_PARAM_DESCS,
    outputs=[("effect_size_results", EffectSizeResults)],
    name="Beta diversity effect size by category.",
    description=(
        "brehhhh"
    )
)

plugin.visualizers.register_function(
    function=plot_power_curve,
    inputs={
        "power_analysis_results": PowerAnalysisResults,
    },
    input_descriptions={
        "power_analysis_results": "Results from power analysis calculations"
    },
    parameters={
        "target_power": Probability,
        "style": Str % Choices({"alpha", "effect_size"})
    },
    parameter_descriptions={
        "target_power": "Value at which to draw horizontal power line.",
        "style": "Whether to use 'alpha' or 'effect_size' as style."
    },
    name="Plot power curve.",
    description=(
        "Plot power curve based on power analysis results. x-axis is total "
        "number of observations and y-axis is power."
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
