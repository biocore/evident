from typing import Any, Iterable
from warnings import warn

import numpy as np
import pandas as pd
from scipy.spatial.distance import squareform


def _listify(x: Any):
    """Convert value to list if it is not already iterable."""
    if not isinstance(x, Iterable):
        return [x]
    else:
        return x


def _check_sample_overlap(ids1: set, ids2: set):
    overlap = ids1.intersection(ids2)
    if ids1 != ids2:
        msg = (
            "Data and metadata do not have the same sample IDs. Using "
            f"{len(overlap)} samples common to both."
        )
        warn(msg)
    return list(overlap)


def _preprocess_input(
    distance_matrix: pd.DataFrame,
    metadata: pd.DataFrame,
    column: str
):
    """Compute intermediate PERMANOVA results not affected by permutations.

    This function is adapted from scikit-bio under the BSD-3 license.
    Original code: https://tinyurl.com/3bwu8h9n
    """
    dm = distance_matrix.loc[metadata.index, metadata.index]
    grouping = metadata[column].to_list()
    sample_size = dm.shape[0]

    # Find the group labels and convert grouping to an integer vector
    # (factor).
    groups, grouping = np.unique(grouping, return_inverse=True)
    num_groups = len(groups)
    tri_idxs = np.triu_indices(sample_size, k=1)
    distances = squareform(dm.values, force="tovector", checks=False)

    return sample_size, num_groups, grouping, tri_idxs, distances
