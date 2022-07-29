from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypedDict


class DistributionDict(TypedDict):
    distribution: str
    params: Dict[str, Any]


class Distribution(ABC):
    @abstractmethod
    def to_dict(self) -> DistributionDict:
        ...


class LogUniform(Distribution):
    def __init__(self, low: float, high: float) -> None:
        self.low = low
        self.high = high

    def to_dict(self) -> DistributionDict:
        return {"distribution": "log_uniform", "params": {"low": self.low, "high": self.high}}


class Uniform(Distribution):
    def __init__(self, low: float, high: float) -> None:
        self.low = low
        self.high = high

    def to_dict(self):
        return {"distribution": "uniform", "params": {"low": self.low, "high": self.high}}


class Categorical(Distribution):
    def __init__(self, choices: List[Any]) -> None:
        self.choices = choices

    def to_dict(self) -> DistributionDict:
        return {"distribution": "categorical", "params": {"choices": self.choices}}


class IntUniform(Distribution):
    def __init__(self, low: int, high: int, step: Optional[int] = 1) -> None:
        self.low = low
        self.high = high
        self.step = step

    def to_dict(self) -> DistributionDict:
        return {"distribution": "int_uniform", "params": {"low": self.low, "high": self.high, "step": self.step}}
