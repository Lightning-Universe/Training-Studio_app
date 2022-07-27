from typing import Any, Dict, Optional

from lightning.app.components.python import TracerPythonScript
from lightning.app.components.training import LightningTrainingComponent, PyTorchLightningScriptRunner

from lightning_hpo.framework.agnostic import BaseObjective


class PyTorchLightningObjective(BaseObjective, PyTorchLightningScriptRunner):

    """This component executes a PyTorch Lightning script
    and injects a callback in the Trainer at runtime in order to start tensorboard server."""

    def __init__(self, *args, logger: str, sweep_id: str, trial_id: int, **kwargs):
        BaseObjective.__init__(self, logger=logger, sweep_id=sweep_id, trial_id=trial_id, **kwargs)
        PyTorchLightningScriptRunner.__init__(self, *args, **kwargs)

    def configure_tracer(self):
        if self.node_rank != 0:
            return BaseObjective.configure_tracer(self)
        else:
            return TracerPythonScript.configure_tracer(self)

    def run(self, params: Optional[Dict[str, Any]] = None, restart_count: int = 0, **kwargs):
        self.params = params
        return PyTorchLightningScriptRunner.run(self, **kwargs)

    @classmethod
    def distributions(cls):
        return None


class ObjectiveLightningTrainingComponent(LightningTrainingComponent):
    def __init__(self, *args, trial_id: int, logger: str, sweep_id: str, **kwargs):
        super().__init__(
            *args,
            script_runner=PyTorchLightningObjective,
            logger=logger,
            sweep_id=sweep_id,
            trial_id=trial_id,
            num_nodes=2,
            **kwargs,
        )
        self.trial_id = trial_id
        self.has_stopped = False
        self.pruned = False
        self.params = None
        self.restart_count = 0
        self.sweep_id = sweep_id
        self.reports = []

    def run(self, params: Optional[Dict[str, Any]] = None, restart_count: int = 0):
        self.params = params
        self.restart_count = restart_count
        super().run(params=params, restart_count=restart_count)

    @property
    def monitor(self):
        return self.ws[0].monitor

    @property
    def best_model_path(self):
        return self.ws[0].best_model_path

    @property
    def best_model_score(self):
        return self.ws[0].best_model_score

    def stop(self):
        for w in self.works():
            w.stop()
        self.has_stopped = True
