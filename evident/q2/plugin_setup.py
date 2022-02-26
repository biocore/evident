import importlib

from qiime2.plugin import (Plugin, MetadataColumn, Categorical, Int, Float,
                           List, Range)
from q2_types.sample_data import SampleData, AlphaDiversity

from evident import __version__
from ._wrappers import (alpha_power_analysis, beta_power_analysis)
from ._format import PowerAnalysisResultsDirectoryFormat as PARsDirFmt
from ._type import PowerAnalysisResults


Probability = Float % Range(0, 1, inclusive_end=False)


plugin = Plugin(
    name="evident",
    version=__version__,
    website="https://github.com/gibsramen/evident",
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
    parameters={
        "sample_metadata": MetadataColumn[Categorical],
        "alpha": List[Probability],
        "power": List[Probability],
        "total_observations": List[Int]
    },
    outputs=[("power_analysis_results", PowerAnalysisResults)],
    name="bruh_fam",
    description="bruh_fam2",
)

plugin.methods.register_function(
    function=beta_power_analysis,
    inputs={
        "beta_diversity": SampleData[AlphaDiversity],
    },
    parameters={
        "sample_metadata": MetadataColumn[Categorical],
        "alpha": List[Probability],
        "power": List[Probability],
        "total_observations": List[Int]
    },
    outputs=[("power_analysis_results", PowerAnalysisResults)],
    name="bruh_fam",
    description="bruh_fam2",
)

plugin.register_semantic_types(PowerAnalysisResults)
plugin.register_semantic_type_to_format(
    PowerAnalysisResults,
    artifact_format=PARsDirFmt
)
plugin.register_formats(PARsDirFmt)

importlib.import_module("evident.q2._transformer")
