from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypedDict

from lightning_hpo.commands.sweep.run import Distributions, Params


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


_DISTRIBUTION = {"uniform": Uniform, "int_uniform": IntUniform, "log_uniform": LogUniform, "categorical": Categorical}


def parse_distributions(distributions: Dict[str, Distributions]) -> Dict[str, Distribution]:
    return {k: _DISTRIBUTION[v.distribution](**v.params.params) for k, v in distributions.items()}


def unparse_distributions(distributions: Optional[Dict[str, Distribution]]) -> Dict[str, Distributions]:
    if not distributions:
        return {}

    dist = {
        k: Distributions(distribution=x.to_dict()["distribution"], params=Params(params=x.to_dict()["params"]))
        for k, x in distributions.items()
    }
    return dist
