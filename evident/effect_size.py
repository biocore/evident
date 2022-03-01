from dataclasses import dataclass
from typing import List

import numpy as np
import pandas as pd


@dataclass
class EffectSizeResult:
    value: float
    metric: str


class EffectSizeResults:
    def __init__(self, results: List[EffectSizeResult])
