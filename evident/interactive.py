import os
import shutil

import numpy as np

from evident.diversity_handler import (_BaseDiversityHandler,
                                       AlphaDiversityHandler,
                                       BetaDiversityHandler)


def create_bokeh_app(diversity_handler: _BaseDiversityHandler,
                     output: os.PathLike, max_levels_per_category: int = 5,
                     exist_ok: bool = False) -> None:
    curr_path = os.path.dirname(__file__)
    support_files = os.path.join(curr_path, "support_files")

    shutil.copytree(support_files, output, dirs_exist_ok=exist_ok)
    data_dir = os.path.join(output, "data")
    os.makedirs(data_dir, exist_ok=exist_ok)

    md = diversity_handler.metadata
    # Get all categorical columns
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
