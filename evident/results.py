from dataclasses import dataclass
from typing import Any, List

import pandas as pd


@dataclass
class EffectSizeResult:
    effect_size: float
    metric: str
    column: str

    def to_dict(self) -> dict:
        res_dict = {
            "effect_size": self.effect_size,
            "metric": self.metric,
            "column": self.column,
        }
        return res_dict


class PairwiseEffectSizeResult(EffectSizeResult):
    def __init__(self, value: float, column: str, group_1: str, group_2: str):
        self.group_1 = group_1
        self.group_2 = group_2
        super().__init__(value, "cohens_d", column)

    def to_dict(self) -> dict:
        res_dict = super().to_dict()
        res_dict["group_1"] = self.group_1
        res_dict["group_2"] = self.group_2
        return res_dict


@dataclass
class PowerAnalysisResult:
    alpha: float
    total_observations: int
    power: float
    effect_size_result: EffectSizeResult
    difference: float

    def to_dict(self) -> dict:
        res_dict = {
            "alpha": self.alpha,
            "total_observations": self.total_observations,
            "power": self.power,
            "effect_size": self.effect_size_result,
            "difference": self.difference
        }
        return res_dict


class _EvidentResults:
    def __init__(self, results: List[Any]):
        self.results = results

    def to_dataframe(self) -> pd.DataFrame:
        df = pd.DataFrame.from_records(
            [x.to_dict() for x in self.results]
        ).reset_index(drop=True)
        return df

    def __next__(self):
        if self._n >= len(self.results):
            raise StopIteration
        result = self.results[self._n]
        self._n += 1
        return result

    def __iter__(self):
        self._n = 0
        return self

    def __len__(self):
        return len(self.results)

    def __getitem__(self, index):
        return self.results[index]


class PowerAnalysisResults(_EvidentResults):
    def __init__(self, results: List[PowerAnalysisResult]):
        super().__init__(results)

    def to_dataframe(self):
        records = []
        for res in self.results:
            this_res_dict = res.to_dict()
            this_effect_size_result = (
                this_res_dict["effect_size"]
                .to_dict()
            )
            this_res_dict.update(this_effect_size_result)
            records.append(this_res_dict)

        return pd.DataFrame.from_records(records)


class EffectSizeResults(_EvidentResults):
    def __init__(self, results: List[EffectSizeResult]):
        super().__init__(results)

    def to_dataframe(sort: bool = True):
        df = super().to_dataframe()
        if sort:
            df = df .sort_values(by=["metric", "effect_size"],
                                 ascending=[True, False])

        return df.reset_index(drop=True)
