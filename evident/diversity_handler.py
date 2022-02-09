from abc import ABC, abstractmethod
from functools import partial
from typing import Callable

import numpy as np
import pandas as pd
from statsmodels.stats.power import tt_ind_solve_power, FTestAnovaPower

# from .exceptions import NoCommonSamplesError
from ._utils import pooled_stdev


class BaseDiversityHandler(ABC):
    def __init__(self, data=None, metadata: pd.DataFrame = None):
        self.data = data
        self.metadata = metadata

    @property
    def samples(self):
        return self.metadata.index.to_list()

    @abstractmethod
    def power_analysis(
        self,
        power_function: Callable,
        alpha: float = None,
        power: float = None
    ):
        """Perform power analysis using this dataset

        NOTE: Only really makes sense when *not* specifying effect size.
              Use diversity for effect size calculation depending on groups.
              Maybe allow specificying difference?

        Observations calculated in _incept_power_solve_function and is
            included in power_function
        """
        val_to_solve = power_function(
            power=power,
            alpha=alpha
        )
        return val_to_solve

    @abstractmethod
    def subset_values(self, ids: list):
        """Get subset of data given list of indices"""
        return

    def _incept_power_solve_function(
        self,
        column: str,
        total_observations: int = None
    ) -> Callable:
        """Create basic function to solve for power.

        :param column: Name of column in metadata to consider
        :type column: str

        :param total_observations: Total number of observations for power
            calculation, defaults to None
        :type total_observations: int

        :returns: Stem of power function based on chosen column
        :rtype: partial function
        """
        if self.metadata[column].dtype != np.dtype("object"):
            raise ValueError("Column must be of dtype object!")

        column_choices = self.metadata[column].unique()
        num_choices = len(column_choices)

        if num_choices == 1:
            raise ValueError("Only one column value!")
        elif num_choices == 2:
            # tt_ind_solve_power uses observations per group
            if total_observations is not None:
                total_observations = total_observations / 2

            power_func = partial(
                tt_ind_solve_power,
                nobs1=total_observations,
                ratio=1.0
            )
            c1, c2 = column_choices
            ids1 = self.metadata[self.metadata[column == c1]].index
            ids2 = self.metadata[self.metadata[column == c2]].index
            mu1 = self.subset_values(ids1)
            mu2 = self.subset_values(ids2)

            effect_size_numerator = np.abs(mu1 - mu2)
        else:
            # FTestAnovaPower uses *total* observations
            power_func = partial(
                FTestAnovaPower().solve_power,
                k_groups=num_choices,
                nobs=total_observations
            )

            all_ids = self.metadata.index
            total_mu = self._subset_values(all_ids).mean()

            # tinyurl.com/4p47ffem
            # sigma_m^2 = sum_{i=1}^G (n_i/N)(mu_i - mu_w)^2
            effect_size_numerator = 0
            for choice in column_choices:
                ids = self.metadata[self.metadata[column == choice]].index
                choice_mu = self._subset_values(ids).mean()
                effect_size_numerator += (
                    len(ids) / len(all_ids)
                    * np.power(choice_mu - total_mu, 2)
                )
            effect_size_numerator = np.sqrt(effect_size_numerator)

        # NOTE: Inefficient w/ above
        values = []
        for option, option_df in self.metadata.groupby(column):
            indices = option_df.index
            values.append(self.subset_values(indices))

        std_p = pooled_stdev(*values)
        effect_size = effect_size_numerator / std_p

        return partial(power_func, effect_size)


class AlphaDiversityHandler(BaseDiversityHandler):
    def __init__(
        self,
        data: pd.Series,
        metadata: pd.DataFrame
    ):
        md_samps = set(metadata.index)
        data_samps = set(data.index)
        samps_in_common = list(md_samps.intersection(data_samps))

        super().__init__(
            data=data.loc[samps_in_common],
            metadata=metadata.loc[samps_in_common]
        )

    def subset_values(self, ids: list):
        return self.metadata.loc[ids]

    def power_analysis(
        self,
        column: str,
        total_observations: int = None,
        difference: float = None,
        alpha: float = None,
        power: float = None
    ):
        power_func = self._incept_power_solve_function(
            column=column,
            total_observation=total_observations
        )

        val = super().power_analysis(
            power_function=power_func,
            alpha=alpha,
            power=power
        )

        return val
