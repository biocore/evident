from typing import List

import pandas as pd
from qiime2 import Metadata
from skbio import DistanceMatrix

from evident import UnivariateDataHandler, BivariateDataHandler
from evident.data_handler import RepeatedMeasuresUnivariateDataHandler as RDH
from evident.effect_size import (effect_size_by_category,
                                 pairwise_effect_size_by_category)


def univariate_power_analysis(
    sample_metadata: Metadata,
    group_column: str,
    data: pd.Series = None,
    data_column: str = None,
    max_levels_per_category: int = 5,
    min_count_per_level: int = 3,
    alpha: list = None,
    power: list = None,
    total_observations: list = None,
    difference: list = None,
) -> pd.DataFrame:
    sample_metadata = sample_metadata.to_dataframe()
    if data is None:
        data = sample_metadata[data_column]
        sample_metadata = sample_metadata.drop(columns=[data_column])
    res = _power_analysis(data, sample_metadata, group_column,
                          UnivariateDataHandler,
                          max_levels_per_category, min_count_per_level,
                          alpha=alpha, power=power,
                          total_observations=total_observations,
                          difference=difference)
    return res


def bivariate_power_analysis(
    data: DistanceMatrix,
    sample_metadata: Metadata,
    group_column: str,
    max_levels_per_category: int = 5,
    min_count_per_level: int = 3,
    alpha: list = None,
    power: list = None,
    total_observations: list = None,
    difference: list = None,
) -> pd.DataFrame:
    sample_metadata = sample_metadata.to_dataframe()
    res = _power_analysis(data, sample_metadata, group_column,
                          BivariateDataHandler,
                          max_levels_per_category, min_count_per_level,
                          alpha=alpha, power=power,
                          total_observations=total_observations,
                          difference=difference)
    return res


def _power_analysis(data, metadata, group_column, handler,
                    max_levels_per_category, min_count_per_level, **kwargs):
    dh = handler(data, metadata, max_levels_per_category,
                 min_count_per_level)
    res = dh.power_analysis(group_column, **kwargs)
    return res.to_dataframe()


def univariate_effect_size_by_category(
    sample_metadata: Metadata,
    group_columns: List[str],
    data: pd.Series = None,
    data_column: str = None,
    pairwise: bool = False,
    n_jobs: int = None,
    max_levels_per_category: int = 5,
    min_count_per_level: int = 3
) -> pd.DataFrame:
    sample_metadata = sample_metadata.to_dataframe()
    if data is None:
        data = sample_metadata[data_column]
        sample_metadata = sample_metadata.drop(columns=[data_column])
    res = _effect_size_by_category(data, sample_metadata,
                                   UnivariateDataHandler, group_columns,
                                   pairwise, n_jobs, max_levels_per_category,
                                   min_count_per_level)
    return res


def bivariate_effect_size_by_category(
    data: DistanceMatrix,
    sample_metadata: Metadata,
    group_columns: List[str],
    pairwise: bool = False,
    n_jobs: int = None,
    max_levels_per_category: int = 5,
    min_count_per_level: int = 3
) -> pd.DataFrame:
    sample_metadata = sample_metadata.to_dataframe()
    res = _effect_size_by_category(data, sample_metadata,
                                   BivariateDataHandler, group_columns,
                                   pairwise, n_jobs, max_levels_per_category,
                                   min_count_per_level)
    return res


def _effect_size_by_category(data, metadata, handler, columns, pairwise,
                             n_jobs, max_levels_per_category,
                             min_count_per_level):
    dh = handler(data, metadata, max_levels_per_category,
                 min_count_per_level)
    if pairwise:
        res = pairwise_effect_size_by_category(dh, columns, n_jobs=n_jobs)
    else:
        res = effect_size_by_category(dh, columns, n_jobs=n_jobs)
    return res.to_dataframe()


def univariate_power_analysis_repeated_measures(
    sample_metadata: Metadata,
    individual_id_column: str,
    state_column: str,
    data: pd.Series = None,
    data_column: str = None,
    subjects: list = None,
    measurements: list = None,
    alpha: list = None,
    correlation: list = None,
    epsilon: list = None,
    max_levels_per_category: int = 5,
    min_count_per_level: int = 3,
) -> pd.DataFrame:
    sample_metadata = sample_metadata.to_dataframe()
    if data is None:
        data = sample_metadata[data_column]
        sample_metadata = sample_metadata.drop(columns=[data_column])
    dh = RDH(data, sample_metadata,
             individual_id_column, max_levels_per_category,
             min_count_per_level)

    results = dh.power_analysis(
        state_column,
        subjects,
        measurements,
        alpha,
        correlation,
        epsilon
    ).to_dataframe()

    return results
