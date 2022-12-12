from abc import ABC, abstractmethod
from typing import Any, Dict, List

from lightning_training_studio.commands.sweep.run import ExperimentConfig


class Algorithm(ABC):
    @abstractmethod
    def register_distributions(self, distributions):
        ...

    @abstractmethod
    def register_experiments(self, experiments: List[ExperimentConfig]):
        ...

    @abstractmethod
    def experiment_start(self, experiment_id: int):
        ...

    @abstractmethod
    def experiment_end(self, experiment_id: int, score: float):
        ...

    @abstractmethod
    def should_prune(self, experiment_id: int, reports: List[float]) -> bool:
        ...

    @abstractmethod
    def get_params(self, experiment_id: int) -> Dict[str, Any]:
        ...
