from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union
from lightning import LightningFlow, LightningWork


class Logger(ABC):

    @abstractmethod
    def on_start(self, sweep_id: str):
        ...

    @abstractmethod
    def on_trial_end(self, score: float, params: Dict[str, Any]):
        ...

    @abstractmethod
    def on_batch_trial_end(self):
        ...

    @abstractmethod
    def connect(self, flow: LightningFlow):
        ...

    @abstractmethod
    def configure_layout(self) -> Dict[str, Any]:
        ...