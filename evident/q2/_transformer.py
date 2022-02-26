import pandas as pd

from .plugin_setup import plugin
from ._format import PowerAnalysisResultDirectoryFormat as PARDirFmt


@plugin.register_transformer
def _1(data: pd.Series) -> PARDirFmt:
    ff = PARDirFmt()
    with ff.open() as fh:
        data.to_csv(fh, sep="\t")
    return ff


@plugin.register_transformer
def _2(ff: PARDirFmt) -> pd.Series:
    return pd.read_table(str(ff)).squeeze()
