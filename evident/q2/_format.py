import qiime2.plugin.model as model


class PowerAnalysisResultsFormat(model.TextFileFormat):
    def validate(self, *args):
        pass


class EffectSizeResultsFormat(model.TextFileFormat):
    def validate(self, *args):
        pass


PowerAnalysisResultsDirectoryFormat = model.SingleFileDirectoryFormat(
    "PowerAnalysisResultsFormat",
    "results.tsv",
    PowerAnalysisResultsFormat
)

EffectSizeResultsDirectoryFormat = model.SingleFileDirectoryFormat(
    "EffectSizeResultsFormat",
    "results.tsv",
    EffectSizeResultsFormat
)
