import pandas as pd
from qiime2.plugin import Metadata
from qiime2 import CategoricalMetadataColumn

from evident import AlphaDiversityHandler


def alpha_power_analysis_single(
    alpha_diversity: pd.Series,
    sample_metadata: CategoricalMetadataColumn,
    alpha: float = None,
    power: float = None,
    total_observations: int = None
) -> pd.Series:
    md = sample_metadata.to_series()
    column = md.name
    adh = AlphaDiversityHandler(alpha_diversity, md.to_frame())
    res = adh.power_analysis(
        column=column,
        total_observations=total_observations,
        alpha=alpha,
        power=power
    )
    return res.to_series()
