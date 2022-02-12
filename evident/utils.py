from typing import Any, Iterable


def listify(x: Any):
    """Convert value to list if it is not already iterable."""
    if not isinstance(x, Iterable):
        return [x]
    else:
        return x
