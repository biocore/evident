from abc import ABC, abstractmethod
from functools import lru_cache, partial
from itertools import product
from typing import Callable, Iterable, Union
from warnings import warn

import numpy as np
import pandas as pd
from skbio import DistanceMatrix
from statsmodels.stats.power import tt_ind_solve_power, FTestAnovaPower

from . import _exceptions as exc
from .results import (CrossSectionalPowerAnalysisResult, PowerAnalysisResults,
                      RepeatedMeasuresPowerAnalysisResult, EffectSizeResult)
from .stats import (calculate_cohens_d, calculate_cohens_f,
                    calculate_pooled_stdev, calculate_eta_squared,
                    calculate_rm_anova_power)
from .utils import _listify, _check_sample_overlap


class _BaseDataHandler(ABC):
    """Abstract class for handling data and metadata."""
    def __init__(
        self,
        data=None,
        metadata: pd.DataFrame = None,
        max_levels_per_category: int = 5,
        min_count_per_level: int = 3,
        individual_id_column: str = None
    ):
        cat_columns = metadata.columns
        if individual_id_column is not None:
            if individual_id_column not in cat_columns:
                raise ValueError(f"{individual_id_column} not in metadata!")
            cat_columns = cat_columns.drop(individual_id_column)
            self.individual_id_column = individual_id_column

        self.data = data
        metadata = metadata.copy()

        cols_to_drop = []
        levels_to_drop = dict()

        warn_msg_num_levels = False
        warn_msg_level_count = False
        for col in cat_columns:
            # Drop non-categorical columns
            if metadata[col].dtype != np.dtype("object"):
                cols_to_drop.append(col)
                continue

            # Drop columns with only one level or more than max
            num_uniq_cols = len(metadata[col].dropna().unique())
            if not (1 < num_uniq_cols <= max_levels_per_category):
                cols_to_drop.append(col)
                warn_msg_num_levels = True
                continue

            # Drop levels that have fewer than min_count_per_level samples
            level_count = metadata[col].value_counts()
            under_thresh = level_count[level_count < min_count_per_level]
            if not under_thresh.empty:
                levels_under_thresh = list(under_thresh.index)
                metadata[col].replace(
                    {x: np.nan for x in levels_under_thresh},
                    inplace=True
                )
                levels_to_drop[col] = levels_under_thresh
                warn_msg_level_count = True

        if warn_msg_num_levels:
            warn(
                "Some categories have been dropped because they had either "
                "only one level or too many. Use the max_levels_per_category "
                "argument to modify this threshold.\n"
                f"Dropped columns: {cols_to_drop}"
            )
        if warn_msg_level_count:
            warn(
                "Some categorical levels have been dropped because they "
                "did not have enough samples. Use the min_count_per_level "
                "argument to modify this threshold.\n"
                f"Dropped levels: {levels_to_drop}"
            )

        self.metadata = metadata.drop(columns=cols_to_drop)

    @property
    def samples(self):
        """Get represented samples."""
        return self.metadata.index.to_list()

    @lru_cache()
    def calculate_effect_size(
        self,
        column: str,
        difference: float = None
    ) -> EffectSizeResult:
        """Get effect size of data differences given column.

        Otherwise, if two categories, return Cohen's d from t-test. If more
        than two categories, return Cohen's f from ANOVA.

        :param column: Column containing categories
        :type column: str

        :param difference: If provided, used as the numerator in effect size
            calculation rather than the difference in means, defaults to None
        :type difference: float

        :returns: Effect size
        :rtype: evident.results.EffectSizeResult
        """
        if self.metadata[column].dtype != np.dtype("object"):
            raise exc.NonCategoricalColumnError(self.metadata[column])

        column_choices = self.metadata[column].dropna().unique()
        num_choices = len(column_choices)

        if num_choices == 1:
            raise exc.OnlyOneCategoryError(self.metadata[column])
        elif num_choices == 2:
            effect_size_func = calculate_cohens_d
            metric = "cohens_d"
        else:
            effect_size_func = calculate_cohens_f
            metric = "cohens_f"

        # Create list of arrays for effect size calculation
        arrays = []
        for choice in column_choices:
            ids = self.metadata[self.metadata[column] == choice].index
            values = self.subset_values(ids)
            arrays.append(values)

        if difference is None:
            result = effect_size_func(*arrays)
        else:
            pooled_stdev = calculate_pooled_stdev(*arrays)
            result = difference / pooled_stdev

        return EffectSizeResult(effect_size=result, metric=metric,
                                column=column)

    def power_analysis(
        self,
        column: str,
        total_observations: int = None,
        difference: float = None,
        alpha: float = None,
        power: float = None
    ) -> Union[CrossSectionalPowerAnalysisResult, PowerAnalysisResults]:
        """Perform power analysis using this dataset.

        Exactly one of total_observations, alpha, or power must be None.

        Arguments can be either single values or sequences of values. If a
            sequence of values is passed for any parameter, power calculations
            will be done on each possible set of argument combinations in the
            Cartesian product set.

        :param column: Name of column in metadata to consider
        :type column: str

        :param difference: Difference between groups to consider, defaults to
            None. If provided, uses the pooled standard deviation as the
            denominator to calculate the effect size with the difference as the
            numerator. Can be either float or sequence of floats.
        :type difference: float or np.array[float]

        :param alpha: Significant level to use in power calculation, defaults
            to None. Can be either float or sequence of floats.
        :type alpha: float or np.array[float]

        :param power: Power level to use in power calculation, defaults to
            None. Can be either float or sequence of floats.
        :type power: float or np.array[float]

        :returns: Results from power analysis
        :rtype: Either CrossSectionalPowerAnalysisResult or
            PowerAnalysisResults
        """
        args = [alpha, power, total_observations]
        none_args = [x is None for x in args]
        if sum(none_args) != 1:  # Check to make sure exactly one arg is None
            raise exc.WrongPowerArguments(*args)

        # If any of the arguments are iterable, perform power analysis on
        #     all possible argument combinations. Otherwise, perform a single
        #     power analysis to solve for the non-provided argument.
        vector_args = map(lambda x: isinstance(x, Iterable), args)
        if any(vector_args):
            power_analysis_func = self._bulk_power_analysis
        else:
            power_analysis_func = self._single_power_analysis

        result = power_analysis_func(
            column=column,
            total_observations=total_observations,
            difference=difference,
            alpha=alpha,
            power=power
        )
        return result

    def _single_power_analysis(
        self,
        column: str,
        total_observations: int = None,
        difference: float = None,
        alpha: float = None,
        power: float = None
    ) -> CrossSectionalPowerAnalysisResult:
        """Compute the power analysis for a single value.

        :param column: Name of column in metadata to consider
        :type column: str

        :param difference: Difference between groups to consider, defaults to
            None. If provided, uses the pooled standard deviation as the
            denominator to calculate the effect size with the difference as the
            numerator.
        :type difference: float

        :param alpha: Significant level to use in power calculation, defaults
            to None.
        :type alpha: float

        :param power: Power level to use in power calculation, defaults to
            None.
        :type power: float

        :returns: Collection of values from power analysis
        :rtype: evident.results.CrossSectionalPowerAnalysisResult
        """
        power_func = self._create_partial_power_func(
            column=column,
            total_observations=total_observations
        )
        effect_size_result = self.calculate_effect_size(column, difference)

        val_to_solve = power_func(power=power, alpha=alpha,
                                  effect_size=effect_size_result.effect_size)

        # If calculating total_observations, check to see if doing t-test
        # If so, multiply by two as tt_ind_solve_power returns number of
        #     observations of sample 1.
        if total_observations is None:
            power_func_name = power_func.func.__qualname__
            if power_func_name == "TTestIndPower.solve_power":
                val_to_solve = np.ceil(val_to_solve) * 2

        args = [alpha, power, total_observations]
        none_args = [x is None for x in args]
        idx = none_args.index(True)

        if idx == 0:
            alpha = val_to_solve
        elif idx == 1:
            power = val_to_solve
        else:
            total_observations = val_to_solve

        results = CrossSectionalPowerAnalysisResult(
            alpha=alpha,
            total_observations=total_observations,
            power=power,
            effect_size_result=effect_size_result,
            difference=difference
        )
        return results

    def _bulk_power_analysis(
        self,
        column: str,
        total_observations: int = None,
        difference: float = None,
        alpha: float = None,
        power: float = None
    ) -> PowerAnalysisResults:
        """Compute the power analysis for a multiple values.

        :param column: Name of column in metadata to consider
        :type column: str

        :param difference: Differences between groups to consider, defaults to
            None. If provided, uses the pooled standard deviation as the
            denominator to calculate the effect size with the difference as the
            numerator.
        :type difference: sequence of floats

        :param alpha: Significance levels to use in power calculation, defaults
            to None.
        :type alpha: sequence of floats

        :param power: Power levels to use in power calculation, defaults to
            None.
        :type power: sequence of floats

        :returns: Collection of values from power analyses
        :rtype: evident.results.PowerAnalysisResults
        """
        # Convert all to list so we can use Cartesian product
        difference = _listify(difference)
        total_observations = _listify(total_observations)
        alpha = _listify(alpha)
        power = _listify(power)
        power_args = [difference, total_observations, alpha, power]

        power_arg_products = product(*power_args)
        results_list = []
        for _diff, _obs, _alpha, _power in power_arg_products:
            results_list.append(self._single_power_analysis(
                column, _obs, _diff, _alpha, _power
            ))
        return PowerAnalysisResults(results_list)

    @abstractmethod
    def subset_values(self, ids: list):
        """Get subset of data given list of indices"""

    @lru_cache()
    def _create_partial_power_func(
        self,
        column: str,
        total_observations: int = None
    ) -> Callable:
        """Create basic function to solve for power.

        Observations arg calculated in _create_partial_power_func and is
            included in power_func. Need to determine whether to use
            t-test or ANOVA as that determines argument to be used.

        Memoized to avoid duplicated computation in the case of multiple
            power analyses.

        :param column: Name of column in metadata to consider
        :type column: str

        :param total_observations: Total number of observations for power
            calculation, defaults to None
        :type total_observations: int

        :returns: Stem of power function based on chosen column
        :rtype: partial function
        """
        if self.metadata[column].dtype != np.dtype("object"):
            raise exc.NonCategoricalColumnError(self.metadata[column])

        column_choices = self.metadata[column].dropna().unique()
        num_choices = len(column_choices)

        if num_choices == 1:
            raise exc.OnlyOneCategoryError(self.metadata[column])
        elif num_choices == 2:
            # tt_ind_solve_power uses observations per group
            if total_observations is not None:
                total_observations = total_observations / 2

            power_func = partial(
                tt_ind_solve_power,
                nobs1=total_observations,
                ratio=1.0,
            )
        else:
            # FTestAnovaPower uses *total* observations
            power_func = partial(
                FTestAnovaPower().solve_power,
                k_groups=num_choices,
                nobs=total_observations,
            )

        return power_func


class UnivariateDataHandler(_BaseDataHandler):
    def __init__(
        self,
        data: pd.Series,
        metadata: pd.DataFrame,
        max_levels_per_category: int = 5,
        min_count_per_level: int = 3,
        **kwargs
    ):
        """Handler for univariate data.

        :param data: Univariate data vector
        :type data: pd.Series

        :param metadata: Sample metadata
        :type metadata: pd.DataFrame

        :param max_levels_per_category: Max number of levels in a category to
            keep. Any categorical columns that have more than this number of
            unique levels will not be saved, defaults to 5.
        :type max_levels_per_category: int

        :param min_count_per_level: Min number of samples in a given category
            level to keep. Any levels that have fewer than this many samples
            will not be saved, defaults to 3.
        :type min_count_per_level: int
        """
        if not isinstance(data, pd.Series):
            raise ValueError("data must be of type pandas.Series")
        if data.isna().any():
            num_nas = data.isna().sum()
            warn(f"data has {num_nas} NAs. Dropping these values.")

        md_samps = set(metadata.index)
        data_samps = set(data.dropna().index)
        samps_in_common = _check_sample_overlap(md_samps, data_samps)

        super().__init__(
            data=data.loc[samps_in_common],
            metadata=metadata.loc[samps_in_common],
            max_levels_per_category=max_levels_per_category,
            min_count_per_level=min_count_per_level,
            **kwargs
        )

    def subset_values(self, ids: list) -> np.array:
        """Get univariate data differences among provided samples."""
        return self.data.loc[ids].values


class RepeatedMeasuresUnivariateDataHandler(UnivariateDataHandler):
    def __init__(
        self,
        data: pd.Series,
        metadata: pd.DataFrame,
        individual_id_column: str,
        max_levels_per_category: int = 5,
        min_count_per_level: int = 3,
    ):
        super().__init__(
            data=data,
            metadata=metadata,
            max_levels_per_category=max_levels_per_category,
            min_count_per_level=min_count_per_level,
            individual_id_column=individual_id_column
        )

    @lru_cache()
    def calculate_effect_size(self, state_column: str) -> EffectSizeResult:
        if self.data.name not in self.metadata.columns:
            long_data = pd.concat([self.data, self.metadata], axis=1)
        else:
            long_data = self.metadata
        wide_data = pd.pivot_table(
            data=long_data,
            index=self.individual_id_column,
            columns=state_column,
            values=self.data.name
        )
        result = calculate_eta_squared(wide_data)

        return EffectSizeResult(effect_size=result, metric="eta_squared",
                                column=state_column)

    def power_analysis(
        self,
        state_column: str,
        subjects: int,
        measurements: int,
        alpha: float,
        correlation: float,
        epsilon: float,
    ):
        effect_size_res = self.calculate_effect_size(state_column)
        args = [subjects, measurements, alpha, correlation, epsilon]
        vector_args = map(lambda x: isinstance(x, Iterable), args)
        if any(vector_args):
            power_analysis_func = self._bulk_power_analysis
        else:
            power_analysis_func = self._single_power_analysis

        results = power_analysis_func(
            effect_size_result=effect_size_res,
            subjects=subjects,
            measurements=measurements,
            alpha=alpha,
            correlation=correlation,
            epsilon=epsilon
        )
        return results

    def _single_power_analysis(
        self,
        effect_size_result: EffectSizeResult,
        subjects: int,
        measurements: int,
        alpha: float = 0.05,
        correlation: float = 0.5,
        epsilon: float = 1.0
    ) -> RepeatedMeasuresPowerAnalysisResult:
        power = calculate_rm_anova_power(
            subjects=subjects,
            measurements=measurements,
            threshold=alpha,
            correlation=correlation,
            epsilon=epsilon,
            effect_size=effect_size_result.effect_size
        )
        result = RepeatedMeasuresPowerAnalysisResult(
            alpha=alpha,
            power=power,
            effect_size_result=effect_size_result,
            subjects=subjects,
            measurements=measurements,
            epsilon=epsilon,
            correlation=correlation,
            total_observations=subjects * measurements
        )
        return result

    def _bulk_power_analysis(
        self,
        effect_size_result: EffectSizeResult,
        subjects=None,
        measurements=None,
        alpha=None,
        correlation=float,
        epsilon=float
    ) -> PowerAnalysisResults:
        alpha = _listify(alpha)
        subjects = _listify(subjects)
        measurements = _listify(measurements)
        correlation = _listify(correlation)
        epsilon = _listify(epsilon)
        power_args = [alpha, subjects, measurements, correlation, epsilon]

        power_arg_products = product(*power_args)
        results_list = []
        for _alpha, _subj, _meas, _corr, _eps in power_arg_products:
            results_list.append(self._single_power_analysis(
                effect_size_result,
                _subj,
                _meas,
                _alpha,
                _corr,
                _eps
            ))
        return PowerAnalysisResults(results_list)


class MultivariateDataHandler(_BaseDataHandler):
    def __init__(
        self,
        data: DistanceMatrix,
        metadata: pd.DataFrame,
        max_levels_per_category: int = 5,
        min_count_per_level: int = 3,
    ):
        """Handler for multivariate data.

        :param data: Multivariate distance matrix
        :type data: skbio.DistanceMatrix

        :param metadata: Sample metadata
        :type metadata: pd.DataFrame

        :param max_levels_per_category: Max number of levels in a category to
            keep. Any categorical columns that have more than this number of
            unique levels will not be saved, defaults to 5.
        :type max_levels_per_category: int
        """
        if not isinstance(data, DistanceMatrix):
            raise ValueError("data must be of type skbio.DistanceMatrix")

        md_samps = set(metadata.index)
        data_samps = set(data.ids)
        samps_in_common = _check_sample_overlap(md_samps, data_samps)

        super().__init__(
            data=data.filter(samps_in_common),
            metadata=metadata.loc[samps_in_common],
            max_levels_per_category=max_levels_per_category,
            min_count_per_level=min_count_per_level,
        )

    def subset_values(self, ids: list) -> np.array:
        """Get multivariate data differences among provided samples."""
        return np.array(self.data.filter(ids).to_series().values)
