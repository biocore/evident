from typing import Any, Iterable
from warnings import warn


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
