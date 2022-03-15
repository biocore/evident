import os
import shutil

import numpy as np

from evident.diversity_handler import (_BaseDiversityHandler,
                                       AlphaDiversityHandler,
                                       BetaDiversityHandler)


def create_bokeh_app(
    diversity_handler: _BaseDiversityHandler,
    output: os.PathLike,
    max_levels_per_category: int = 5,
    exist_ok: bool = False
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

    :param exist_ok: Whether to allow intermediate directories to be created
        and existing data to be overwritten, defaults to False
    :type exist_ok: bool
    """
    curr_path = os.path.dirname(__file__)
    support_files = os.path.join(curr_path, "support_files")

    # Copy support files (Bokeh template + script) and data directory
    shutil.copytree(support_files, output, dirs_exist_ok=exist_ok)
    data_dir = os.path.join(output, "data")
    os.makedirs(data_dir, exist_ok=exist_ok)

    md = diversity_handler.metadata
    # Get all valid categorical columns and save metadata to data dir
    valid_cols = [
        x for x in md.columns
        if md[x].dtype == np.dtype("object")
        and 1 < len(md[x].unique()) <= max_levels_per_category
    ]
    md_loc = os.path.join(data_dir, "metadata.tsv")
    md[valid_cols].to_csv(md_loc, sep="\t", index=True)

    data = diversity_handler.data
    if isinstance(diversity_handler, AlphaDiversityHandler):
        data_loc = os.path.join(data_dir, "diversity.alpha.tsv")
        data.to_csv(data_loc, sep="\t", index=True)
    elif isinstance(diversity_handler, BetaDiversityHandler):
        data_loc = os.path.join(data_dir, "diversity.beta.lsmat")
        data.write(data_loc)
    else:
        raise ValueError("No valid data found!")
