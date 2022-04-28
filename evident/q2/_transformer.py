import pandas as pd

from .plugin_setup import plugin
from ._format import PowerAnalysisResultsFormat as PARsFmt
from ._format import EffectSizeResultsFormat as ERsFmt


@plugin.register_transformer
def _1(data: pd.DataFrame) -> (PARsFmt):
    ff = PARsFmt()
    with ff.open() as fh:
        data.to_csv(fh, sep="\t", index=True, header=True)
    return ff


@plugin.register_transformer
def _2(ff: PARsFmt) -> (pd.DataFrame):
    return pd.read_table(str(ff), sep="\t", index_col=0)


@plugin.register_transformer
def _3(data: pd.DataFrame) -> (ERsFmt):
    ff = ERsFmt()
    with ff.open() as fh:
        data.to_csv(fh, sep="\t", index=True, header=True)
    return ff


@plugin.register_transformer
def _4(ff: ERsFmt) -> (pd.DataFrame):
    return pd.read_table(str(ff), sep="\t", index_col=0)
