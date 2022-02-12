from typing import Any, Iterable


def listify(x: Any):
    if not isinstance(x, Iterable):
        return [x]
    else:
        return x
