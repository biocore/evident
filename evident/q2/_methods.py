from typing import List

import pandas as pd
from qiime2 import CategoricalMetadataColumn, Metadata
from skbio import DistanceMatrix

from evident import AlphaDiversityHandler, BetaDiversityHandler
from evident.exploration import (effect_size_by_category,
                                 pairwise_effect_size_by_category)


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
    beta_diversity: DistanceMatrix,
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


def alpha_effect_size_by_category(
    alpha_diversity: pd.Series,
    sample_metadata: Metadata,
    columns: List[str],
    pairwise: bool = False
) -> pd.DataFrame:
    res = _effect_size_by_category(alpha_diversity, sample_metadata,
                                   AlphaDiversityHandler, columns, pairwise)
    return res


def beta_effect_size_by_category(
    beta_diversity: DistanceMatrix,
    sample_metadata: Metadata,
    columns: List[str],
    pairwise: bool = False
) -> pd.DataFrame:
    res = _effect_size_by_category(beta_diversity, sample_metadata,
                                   BetaDiversityHandler, columns, pairwise)
    return res


def _effect_size_by_category(data, metadata, handler, columns, pairwise):
    dh = handler(data, metadata.to_dataframe())
    if pairwise:
        df = pairwise_effect_size_by_category(dh, columns)
    else:
        df = effect_size_by_category(dh, columns)
    return df
