import pandas as pd

from .plugin_setup import plugin
from ._format import PowerAnalysisResultFormat as PARFmt


@plugin.register_transformer
def _1(data: pd.Series) -> (PARFmt):
    ff = PARFmt()
    with ff.open() as fh:
        data.to_csv(fh, sep="\t", index=True, header=True)
    return ff


@plugin.register_transformer
def _2(ff: PARFmt) -> (pd.Series):
    return pd.read_table(str(ff), sep="\t", index_col=0).squeeze()


@plugin.register_transformer
def _3(ff: PARFmt) -> (pd.DataFrame):
    return pd.read_table(str(ff), sep="\t", index_col=0)
