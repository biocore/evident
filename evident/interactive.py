import os
import shutil
from warnings import warn

import numpy as np

from evident.diversity_handler import (_BaseDiversityHandler,
                                       AlphaDiversityHandler,
                                       BetaDiversityHandler)


def create_bokeh_app(
    diversity_handler: _BaseDiversityHandler,
    output: os.PathLike,
    max_levels_per_category: int = 5,
    min_count_per_level: int = 3
) -> None:
    """Creates interactive power analysis using Bokeh.

    :param diversity_handler: Handler with diversity data
    :type diversity_handler: evident.diversity_handler._BaseDiversityHandler

    :param output: Location to create Bokeh app
    :type output: os.PathLike

    :param max_levels_per_category: Max number of levels in a category to
        keep. Any categorical columns that have more than this number of
        unique levels will not be saved, defaults to 5.
    :type max_levels_per_category: int

    :param min_count_per_level: Min number of samples in a given category
        level to keep. Any levels that have fewer than this many samples
        will not be saved, defaults = 3.
    """
    curr_path = os.path.dirname(__file__)
    support_files = os.path.join(curr_path, "support_files")

    # Copy support files (Bokeh template + script) and data directory
    shutil.copytree(support_files, output)
    data_dir = os.path.join(output, "data")
    os.mkdir(data_dir)

    # Process metadata
    md = diversity_handler.metadata.copy()
    cols_to_drop = []
    warn_msg_num_levels = False
    warn_msg_level_count = False
    for col in md.columns:
        # Drop non-categorical columns
        if md[col].dtype != np.dtype("object"):
            cols_to_drop.append(col)
            continue

        # Drop columns with only one level or more than max
        if not (1 < len(md[col].dropna().unique()) <= max_levels_per_category):
            cols_to_drop.append(col)
            warn_msg_num_levels = True
            continue

        # Drop levels that have fewer than min_count_per_level samples
        level_count = md[col].value_counts()
        under_thresh = level_count[level_count < min_count_per_level]
        if not under_thresh.empty:
            levels_under_thresh = list(under_thresh.index)
            md[col].replace(
                {x: np.nan for x in levels_under_thresh},
                inplace=True
            )
            warn_msg_level_count = True

    if warn_msg_num_levels:
        warn(
            "Some categories have been dropped because they had either only "
            "one level or too many. Use the max_levels_per_category "
            "argument to modify this threshold."
        )
    if warn_msg_level_count:
        warn(
            "Some categorical levels have been dropped because they "
            "did not have enough samples. Use the min_count_per_level "
            "argument to modify this threshold."
        )

    md_loc = os.path.join(data_dir, "metadata.tsv")
    md.drop(columns=cols_to_drop).to_csv(md_loc, sep="\t", index=True)

    data = diversity_handler.data
    if isinstance(diversity_handler, AlphaDiversityHandler):
        data_loc = os.path.join(data_dir, "diversity.alpha.tsv")
        data.to_csv(data_loc, sep="\t", index=True)
    elif isinstance(diversity_handler, BetaDiversityHandler):
        data_loc = os.path.join(data_dir, "diversity.beta.lsmat")
        data.write(data_loc)
    else:
        raise ValueError("No valid data found!")
