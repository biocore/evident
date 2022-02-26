import qiime2.plugin.model as model


class PowerAnalysisResultFormat(model.TextFileFormat):
    def validate(self, *args):
        pass


class PowerAnalysisResultsFormat(model.TextFileFormat):
    def validate(self, *args):
        pass


PowerAnalysisResultDirectoryFormat = model.SingleFileDirectoryFormat(
    "PowerAnalysisResultFormat",
    "result.tsv",
    PowerAnalysisResultFormat
)

PowerAnalysisResultsDirectoryFormat = model.SingleFileDirectoryFormat(
    "PowerAnalysisResultsFormat",
    "results.tsv",
    PowerAnalysisResultsFormat
)
