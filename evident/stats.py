import numpy as np
import pandas as pd
from scipy import stats


def calculate_pooled_stdev(*arrays) -> float:
    """Compute pooled standard deviation from multiple arrays.

    https://en.wikipedia.org/wiki/Pooled_variance

    :param arrays: All arrays to pool
    :type arrays: np.ndarray, np.ndarray, ...

    :returns: Pooled standard deviation
    :rtype: float
    """
    pooled_variance_numerator = 0
    lengths = []
    k = len(arrays)

    for array in arrays:
        sample_variance = np.var(array, ddof=1)  # delta DF = 1 for unbiased
        pooled_variance_numerator += sample_variance * (len(array) - 1)
        lengths.append(len(array))

    pooled_variance_denominator = sum(lengths) - k
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


def calculate_cohens_f(*arrays) -> float:
    """Calculate Cohen's f using pooled standard deviation.

    tinyurl.com/4p47ffem
    sigma_m^2 = sum_{i=1}^G (n_i/N)(mu_i - mu_w)^2

    :param arrays: All arrays to pool
    :type arrays: np.ndarray, np.ndarray, ...

    :returns: Cohen's f effect size
    :rtype: float
    """
    pooled_std = calculate_pooled_stdev(*arrays)

    concat_array = np.concatenate(arrays)
    mu_total = np.mean(concat_array)

    effect_size_numerator = 0
    for array in arrays:
        mu_group = np.mean(array)
        effect_size_numerator += (
            len(array) / len(concat_array)
            * np.power(mu_group - mu_total, 2)
        )
    effect_size_numerator = np.sqrt(effect_size_numerator)

    return effect_size_numerator/pooled_std


def calculate_eta_squared(data: pd.DataFrame) -> float:
    """Calculate eta squared for repeated measures ANOVA.

    Resource for eta_squared calculations: tinyurl.com/ycktzet3

    eta2 = SS_cond / (SS_cond + SS_error)
    SS_error = SS_within - SS_subj
    SS_cond = sum_i^k (n_i(x_i - x)^2
    SS_within = sum(xi_1 - x1)^2 + sum(xi2 - x2)^2 ... + sum(xik - xk)^2

    :param data: Repeated measures data. Index is each subject, columns are
        each group. Data should have no missing values.
    :type data: pd.DataFrame

    :returns: Effect size as eta_squared
    :rtype: float
    """
    if data.isna().any().any():
        raise ValueError(
            "Cannot calculate effect size of repeated measures with missing "
            "values."
        )
    k = data.shape[1]  # number of groups
    mu_total = np.mean(data.values.ravel())

    ss_within = data.apply(
        lambda x: np.power(x - np.mean(x), 2),
        axis=0
    ).sum().sum()

    ss_subj = data.apply(
        lambda x: np.power(np.mean(x) - mu_total, 2),
        axis=1
    ).sum() * k

    subjs_per_cond = [data.shape[0]]*k
    ss_cond = np.dot(
        data.apply(
            lambda x: np.power(np.mean(x) - mu_total, 2),
            axis=0
        ),
        subjs_per_cond
    )

    ss_error = ss_within - ss_subj
    eta_sq = ss_cond / (ss_cond + ss_error)

    return eta_sq


def calculate_rm_anova_power(
    subjects: int,
    measurements: int,
    threshold: float,
    correlation: float,
    epsilon: float,
    effect_size: float
) -> float:
    """Calculate power for a repeated measures ANOVA.

    :param subjects: Number of subjects (same for all classes)
    :type subjects: int

    :param measurements: Number of measurements per subject (same for all
        subjects)
    :type measurements: int

    :param threshold: Significance level to reject null hypothesis
    :type threshold: float

    :param correlation: Correlation between repeated measurements
    :type correlation: float

    :param epsilon: Adjustment for sphericity
    :type epsilon: float

    :param effect_size: Effect size as eta-squared of differences
    :type effect_size: float

    :returns: Probability of rejecting null hypothesis given that the
        alternative hypothesis is true
    :rtype: float
    """
    dm = (measurements - 1) * epsilon
    ds = (subjects - 1) * dm
    f = np.abs(effect_size) / (1 - np.abs(effect_size))
    x = f * measurements * subjects * epsilon
    location = x / (1 - correlation)
    q = stats.f.ppf(1 - threshold, dm, ds)
    power = stats.ncf.sf(q, dm, ds, location)
    return power
