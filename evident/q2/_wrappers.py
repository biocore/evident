import pandas as pd
from qiime2.plugin import Metadata

from evident import AlphaDiversityHandler


def alpha_power_analysis_single(
    alpha_diversity: pd.Series,
    sample_metadata: pd.DataFrame,
    column: str,
    alpha: float = None,
    power: float = None,
    total_observations: int = None
) -> pd.Series:
    adh = AlphaDiversityHandler(alpha_diversity, sample_metadata)
    res = adh.power_analysis(
        column=column,
        total_observations=total_observbations,
        alpha=alpha,
        power=power
    )
    return res.to_series()
