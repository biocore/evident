import pandas as pd
from qiime2 import CategoricalMetadataColumn

from evident import AlphaDiversityHandler, BetaDiversityHandler


def alpha_power_analysis(
    alpha_diversity: pd.Series,
    sample_metadata: CategoricalMetadataColumn,
    alpha: list = None,
    power: list = None,
    total_observations: list = None
) -> pd.DataFrame:
    res = _power_analysis(alpha_diversity, sample_metadata,
                          AlphaDiversityHandler, alpha=alpha, power=power,
                          total_observations=total_observations)
    return res


def beta_power_analysis(
    beta_diversity: pd.Series,
    sample_metadata: CategoricalMetadataColumn,
    alpha: list = None,
    power: list = None,
    total_observations: list = None
) -> pd.DataFrame:
    res = _power_analysis(beta_diversity, sample_metadata,
                          BetaDiversityHandler, alpha=alpha, power=power,
                          total_observations=total_observations)
    return res


def _power_analysis(data, metadata, handler, **kwargs):
    md = metadata.to_series()
    column = md.name
    dh = handler(data, md.to_frame())
    res = dh.power_analysis(column, **kwargs)
    return res.to_dataframe()
