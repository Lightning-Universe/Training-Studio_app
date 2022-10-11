from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from lightning import LightningFlow
from lightning.app.utilities.tracer import Tracer


class Logger(ABC):
    def on_after_trial_start(self, sweep_id: str):
        ...

    @abstractmethod
    def on_after_trial_end(
        self, sweep_id: str, trial_id: int, monitor: Optional[str], score: Optional[float], params: Dict[str, Any]
    ):
        ...

    @abstractmethod
    def connect(self, flow: LightningFlow):
        ...

    @abstractmethod
    def configure_layout(self) -> Dict[str, Any]:
        ...

    @abstractmethod
    def configure_tracer(self, tracer, sweep_id: str, trial_id: int, trial_name: str, params: Dict[str, Any]):
        ...

    @abstractmethod
    def get_url(self, trial_id: int) -> Optional[str]:
        ...


class NoneLogger(Logger):
    def on_after_trial_start(self, sweep_id: str):
        pass

    def on_after_trial_end(self, *args, **kwargs):
        pass

    def connect(self, flow: LightningFlow):
        pass

    def configure_layout(self) -> List:
        return []

    def configure_tracer(self, tracer, sweep_id: str, trial_id: int, params: Dict[str, Any]):
        return Tracer()

    def get_url(self, trial_id: int) -> Optional[str]:
        pass
