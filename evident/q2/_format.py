import qiime2.plugin.model as model


class PowerAnalysisResultFormat(model.TextFileFormat):
    def _validate(self):
        pass


PowerAnalysisResultDirectoryFormat = model.SingleFileDirectoryFormat(
    "PowerAnalysisResultFormat",
    "result.tsv",
    PowerAnalysisResultFormat
)
