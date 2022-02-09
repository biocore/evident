import numpy as np


def calculate_pooled_stdev(*arrays) -> float:
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
        corrected_lengths.append(len(array))

    pooled_variance_denominator = sum(corrected_lengths) - k
    pooled_variance = pooled_variance_numerator / pooled_variance_denominator

    return np.sqrt(pooled_variance)


def calculate_cohens_d(values_1: np.ndarray, values_2: np.ndarray) -> float:
    """Calculate Cohen's d using pooled standard deviation.

    :param values_1: First array of values
    :type values_1: np.ndarray

    :param values_2: Second array of values
    :type values_2: np.ndarray

    :returns: Cohen's d effect size
    :rtype: float
    """
    pooled_std = calculate_pooled_stdev(values_1, values_2)
    mu_1 = np.mean(values_1)
    mu_2 = np.mean(values_2)
    return np.abs(mu_1 - mu_2)/pooled_std
