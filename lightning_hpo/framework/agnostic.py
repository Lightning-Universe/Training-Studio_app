from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import optuna
from lightning.app.components.python import TracerPythonScript

from lightning_hpo.loggers import LoggerType


class BaseObjective(TracerPythonScript, ABC):
    def __init__(self, *args, logger: str, sweep_id: str, trial_id, **kwargs):
        super().__init__(*args, raise_exception=True, **kwargs)
        self.trial_id = trial_id
        self.best_model_score = None
        self.best_model_path = None
        self.params = None
        self.has_told_study = False
        self.reports = []
        self.flow_reports = []
        self.pruned = False
        self.logger = logger
        self._url = None
        self.sweep_id = sweep_id
        self.monitor = None

    def configure_tracer(self):
        assert self.params
        tracer = super().configure_tracer()
        LoggerType(self.logger).get_logger().configure_tracer(
            tracer, params=self.params, sweep_id=self.sweep_id, trial_id=self.trial_id
        )
        return tracer

    def run(self, params: Optional[Dict[str, Any]] = None, restart_count: int = 0):
        self.params = params
        return super().run(params=params)

    @abstractmethod
    def distributions() -> Dict[str, optuna.distributions.BaseDistribution]:
        pass
