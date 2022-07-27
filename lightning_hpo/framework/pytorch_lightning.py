from lightning_hpo.objective import BaseObjective
from lightning.app.components.training import PyTorchLightningScriptRunner
from lightning.app.components.training import LightningTrainingComponent
from typing import Dict, Any

class PyTorchLightningObjective(PyTorchLightningScriptRunner):

    """This component executes a PyTorch Lightning script
    and injects a callback in the Trainer at runtime in order to start tensorboard server."""

    def __init__(self, *args, logger: str, sweep_id: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logger
        self.sweep_id = sweep_id

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
            **kwargs,
        )
        self.trial_id = trial_id
        self.has_stopped = False
        self.pruned = False
        self.params = None
        self.restart_count = 0
        self.sweep_id = sweep_id

    def run(self, params: Dict[str, Any], restart_count: int):
        self.params = params
        self.restart_count = restart_count
        super().run(params=params, restart_count=restart_count)

    def stop(self):
        for w in self.works():
            w.stop()
        self.has_stopped = True