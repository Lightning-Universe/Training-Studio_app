import os
import subprocess
import sys
import uuid
from abc import ABC
from typing import Any, Dict, Optional, TypedDict

from lightning.app.components.python import TracerPythonScript
from lightning.app.utilities.app_helpers import is_overridden

from lightning_training_studio.loggers import LoggerType


class ObjectiveResult(TypedDict):
    monitor: str
    score: float
    checkpoint: Optional[str]


class Objective(TracerPythonScript, ABC):
    def objective(self, *args, **kwargs):
        """Override with your own objective logic"""

    def __init__(
        self,
        *args,
        logger: str,
        sweep_id: str,
        experiment_id,
        experiment_name: str,
        raise_exception: bool = False,
        function_name: str = "objective",
        num_nodes: int = 1,  # TODO # Add support for multi node
        last_model_path: Optional[str] = None,
        pip_install_source: bool = False,
        **kwargs,
    ):
        super().__init__(*args, raise_exception=raise_exception, **kwargs)
        self.experiment_id = experiment_id
        self.experiment_name = experiment_name
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
        self.function_name = function_name
        self.has_stored = False
        self.num_nodes = num_nodes
        self.progress = None
        self.last_model_path = last_model_path
        self.pip_install_source = pip_install_source
        self._rootwd = os.getcwd()

    def configure_tracer(self):
        assert self.params is not None
        tracer = super().configure_tracer()
        LoggerType(self.logger).get_logger().configure_tracer(
            tracer,
            params=self.params,
            sweep_id=self.sweep_id,
            experiment_id=self.experiment_id,
            experiment_name=self.experiment_name,
        )
        return tracer

    def run(self, params: Optional[Dict[str, Any]] = None, restart_count: int = 0):
        if self.pip_install_source:
            os.chdir(self._rootwd)
            uid = uuid.uuid4().hex[:8]
            dirname = f"uploaded-{uid}"
            os.makedirs(dirname)
            os.chdir(dirname)
        self.params = params or {}
        if is_overridden("objective", self, Objective):
            self.objective(**self.params)
        else:
            return super().run(params=params)

    def on_before_run(self):
        if self.pip_install_source:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])

    def on_after_run(self, global_scripts: Any):
        objective_fn = global_scripts.get(self.function_name, None)
        if objective_fn:
            res = objective_fn(**self.params)
            if isinstance(res, (int, float)):
                self.monitor = "score"
                self.best_model_score = round(res, 4)
            elif isinstance(res, dict):
                assert isinstance(res, ObjectiveResult)
        super().on_after_run(global_scripts)
