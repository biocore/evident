import numpy as np


def pooled_stdev(*arrays) -> float:
    """Compute pooled standard deviation from multiple arrays.

    https://en.wikipedia.org/wiki/Pooled_variance

    :param arrays: All arrays to pool
    :type arrays: np.ndarray, np.ndarray, ...

    :returns: Pooled standard deviation
    :rtype: float
    """
    pooled_variance_numerator = 0
    corrected_lengths = []
    k = len(arrays)

    for array in arrays:
        sample_variance = np.var(array, ddof=1)  # delta DF = 1 for unbiased
        pooled_variance_numerator += sample_variance * (len(array) - 1)
        corrected_lengths.append(len(array) - 1)

    pooled_variance_denominator = sum(corrected_lengths) - k
    pooled_variance = pooled_variance_numerator / pooled_variance_denominator

    return np.sqrt(pooled_variance)
