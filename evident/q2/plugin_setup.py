import importlib

from qiime2.plugin import (Plugin, MetadataColumn, Categorical, Int, Float,
                           Metadata)
from q2_types.sample_data import SampleData, AlphaDiversity

from evident import __version__
from ._wrappers import alpha_power_analysis_single
from ._format import PowerAnalysisResultDirectoryFormat as PARDirFmt
from ._type import PowerAnalysisResult


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
    outputs=[('power_analysis_result', PowerAnalysisResult)],
    name="bruh",
    description="bruh2",
)

plugin.register_semantic_types(PowerAnalysisResult)
plugin.register_semantic_type_to_format(
    PowerAnalysisResult,
    artifact_format=PARDirFmt
)
plugin.register_formats(PARDirFmt)
importlib.import_module("evident.q2._transformer")
