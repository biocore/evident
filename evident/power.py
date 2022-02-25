from dataclasses import dataclass
from typing import List

import pandas as pd


@dataclass
class PowerAnalysisResult:
    alpha: float
    total_observations: int
    power: float
    effect_size: float
    difference: float

    def to_dict(self) -> dict:
        return {
            "alpha": self.alpha,
            "total_observations": self.total_observations,
            "power": self.power,
            "effect_size": self.effect_size,
            "difference": self.difference
        }


class PowerAnalysisResults:
    def __init__(self, results: List[PowerAnalysisResult]):
        self.results = results

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame.from_records([x.to_dict() for x in self.results])

    def __next__(self):
        if self._n >= len(self.results):
            raise StopIteration
        result = self.results[self._n]
        self._n += 1
        return result

    def __iter__(self):
        self._n = 0
        return self

    def __str__(self):
        return self.results

    def __len__(self):
        return len(self.results)

    def __getitem__(self, index):
        return self.results[index]
