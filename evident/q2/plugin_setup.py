import importlib

from qiime2.plugin import (Plugin, MetadataColumn, Categorical, Int, Float,
                           List)
from q2_types.sample_data import SampleData, AlphaDiversity

from evident import __version__
from ._wrappers import (alpha_power_analysis_single,
                        alpha_power_analysis_multiple)
from ._format import PowerAnalysisResultDirectoryFormat as PARDirFmt
from ._format import PowerAnalysisResultsDirectoryFormat as PARsDirFmt
from ._type import PowerAnalysisResult, PowerAnalysisResults


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
    function=alpha_power_analysis_single,
    inputs={
        "alpha_diversity": SampleData[AlphaDiversity],
    },
    parameters={
        "sample_metadata": MetadataColumn[Categorical],
        "alpha": Float,
        "power": Float,
        "total_observations": Int
    },
    outputs=[("power_analysis_result", PowerAnalysisResult)],
    name="bruh",
    description="bruh2",
)

plugin.methods.register_function(
    function=alpha_power_analysis_multiple,
    inputs={
        "alpha_diversity": SampleData[AlphaDiversity],
    },
    parameters={
        "sample_metadata": MetadataColumn[Categorical],
        "alpha": List[Float],
        "power": List[Float],
        "total_observations": List[Int]
    },
    outputs=[("power_analysis_results", PowerAnalysisResults)],
    name="bruh_fam",
    description="bruh_fam2",
)

plugin.register_semantic_types(PowerAnalysisResult)
plugin.register_semantic_type_to_format(
    PowerAnalysisResult,
    artifact_format=PARDirFmt
)
plugin.register_formats(PARDirFmt)

plugin.register_semantic_types(PowerAnalysisResults)
plugin.register_semantic_type_to_format(
    PowerAnalysisResults,
    artifact_format=PARsDirFmt
)
plugin.register_formats(PARsDirFmt)

importlib.import_module("evident.q2._transformer")
