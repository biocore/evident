import qiime2.plugin.model as model


class PowerAnalysisResultsFormat(model.TextFileFormat):
    def validate(self, *args):
        pass


PowerAnalysisResultsDirectoryFormat = model.SingleFileDirectoryFormat(
    "PowerAnalysisResultsFormat",
    "results.tsv",
    PowerAnalysisResultsFormat
)
