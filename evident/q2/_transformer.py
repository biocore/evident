import pandas as pd

from .plugin_setup import plugin
from ._format import PowerAnalysisResultsFormat as PARsFmt


@plugin.register_transformer
def _1(data: pd.DataFrame) -> (PARsFmt):
    ff = PARsFmt()
    with ff.open() as fh:
        data.to_csv(fh, sep="\t", index=True, header=True)
    return ff


@plugin.register_transformer
def _2(ff: PARsFmt) -> (pd.DataFrame):
    return pd.read_table(str(ff), sep="\t", index_col=0)
