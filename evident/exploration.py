from itertools import combinations

import pandas as pd

from evident.diversity_handler import _BaseDiversityHandler
from evident.stats import calculate_cohens_d


def effect_size_by_category(
    diversity_handler: _BaseDiversityHandler,
    columns: list = None,
) -> pd.DataFrame:
    """Compute effect size for a set of columns.

    Output DataFrame has as index the argument columns. DataFrame columns are
    'metric' and 'value'. Metric is either 'cohens_d' or 'cohens_f' if the
    given category has 2 or more than 2 levels, respectively. 'value' has the
    numeric effect size. Sorts output first by Cohen's d -> f and then effect
    size in decreasing order.

    :param diversity_handler: Either an alpha or beta DiversityHandler
    :type diversity_handler: evident.diversity_handler._BaseDiversityHandler

    :param columns: Columns to use for effect size calculations
    :type columns: List[str]

    :returns: DataFrame of effect size per category
    :rtype: pd.DataFrame
    """
    _check_columns(columns)
    dh = diversity_handler
    effect_size_dict = dict()

    for col in columns:
        num_choices = len(dh.metadata[col].unique())
        effect_size = dh.calculate_effect_size(col)
        if num_choices == 2:
            metric = "cohens_d"
        else:
            metric = "cohens_f"
        effect_size_dict[col] = {"metric": metric, "value": effect_size}

    # Sort by metric first (d -> f) then value in descending order
    effect_size_df = pd.DataFrame.from_dict(effect_size_dict, orient="index")
    effect_size_df.index.name = "column"
    effect_size_df = effect_size_df.sort_values(by=["metric", "value"],
                                                ascending=[True, False])
    effect_size_df = effect_size_df.reset_index(drop=False)

    return effect_size_df


def pairwise_effect_size_by_category(
    diversity_handler: _BaseDiversityHandler,
    columns: list = None
) -> pd.DataFrame:
    """Compute effect size for a set of columns using pairwise comparisons.

    Output DataFrame has no index. DataFrame columns are 'column', 'group_1',
    'group_2', and 'cohens_d'. 'column' has the column from which each row's
    pairwise comparison arises. 'group_1' has the first level of the category
    in 'column' while 'group_2' has the second level of the category in
    'column'. 'cohens_d' has the effect size of each comparison. Output is
    sorted by decreasing 'cohens_d'.

    :param diversity_handler: Either an alpha or beta DiversityHandler
    :type diversity_handler: evident.diversity_handler._BaseDiversityHandler

    :param columns: Columns to use for effect size calculations
    :type columns: List[str]

    :returns: DataFrame of effect size per pairwise comparison
    :rtype: pd.DataFrame
    """
    _check_columns(columns)
    dh = diversity_handler
    effect_size_records = []

    for col in columns:
        values_dict = dict()

        # Get all index sets here to avoid redundant computation
        grp_dfs = (dh.metadata .groupby(col))
        for grp, _df in grp_dfs:
            values_dict[grp] = dh.subset_values(_df.index)

        for grp1, grp2 in combinations(values_dict.keys(), 2):
            vals1 = values_dict[grp1]
            vals2 = values_dict[grp2]
            effect_size = calculate_cohens_d(vals1, vals2)
            effect_size_records.append((col, grp1, grp2, effect_size))

    effect_size_df = pd.DataFrame.from_records(effect_size_records)
    effect_size_df.columns = ["column", "group_1", "group_2", "cohens_d"]

    return effect_size_df.sort_values(by="cohens_d", ascending=False)


def _check_columns(columns) -> None:
    """Check to make sure a list of columns has been passed."""
    if columns is None:
        raise ValueError("Must provide list of columns!")
