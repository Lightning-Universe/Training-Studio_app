from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union
from lightning import LightningFlow, LightningWork


class Logger(ABC):

    def on_trial_start(self, sweep_id: str):
        ...

    @abstractmethod
    def on_trial_end(self, sweep_id: str, trial_id: int, monitor: str, score: float, params: Dict[str, Any]):
        ...

    @abstractmethod
    def connect(self, flow: LightningFlow):
        ...

    @abstractmethod
    def configure_layout(self) -> Dict[str, Any]:
        ...

    @abstractmethod
    def configure_tracer(self, tracer, sweep_id: str, trial_id: int, params: Dict[str, Any]):
        ...