from abc import ABC, abstractmethod
from typing import Any, Dict, List

from lightning_hpo.commands.sweep.run import ExperimentConfig


class Algorithm(ABC):
    @abstractmethod
    def register_distributions(self, distributions):
        ...

    @abstractmethod
    def register_experiments(self, trials: List[ExperimentConfig]):
        ...

    @abstractmethod
    def trial_start(self, trial_id: int):
        ...

    @abstractmethod
    def trial_end(self, trial_id: int, score: float):
        ...

    @abstractmethod
    def should_prune(self, trial_id: int, reports: List[float]) -> bool:
        ...

    @abstractmethod
    def get_params(self, trial_id: int) -> Dict[str, Any]:
        ...
