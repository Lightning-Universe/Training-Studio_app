from typing import Any, Dict, Optional

from lightning.app.components.python import TracerPythonScript
from lightning.app.components.training import LightningTrainingComponent, PyTorchLightningScriptRunner

from lightning_hpo.framework.agnostic import Objective


class PyTorchLightningObjective(Objective, PyTorchLightningScriptRunner):

    """This component executes a PyTorch Lightning script
    and injects a callback in the Trainer at runtime in order to start tensorboard server."""

    def __init__(self, *args, logger: str, sweep_id: str, trial_id: int, num_nodes: int, **kwargs):
        Objective.__init__(self, logger=logger, sweep_id=sweep_id, trial_id=trial_id, **kwargs)
        PyTorchLightningScriptRunner.__init__(self, *args, num_nodes=num_nodes, **kwargs)
        self.progress = None

    def configure_tracer(self):
        if self.node_rank == 0:
            tracer = Objective.configure_tracer(self)
            return self.add_progress_tracking(tracer)
        return TracerPythonScript.configure_tracer(self)

    def run(self, params: Optional[Dict[str, Any]] = None, restart_count: int = 0, **kwargs):
        self.params = params
        return PyTorchLightningScriptRunner.run(self, params=params, **kwargs)

    def on_after_run(self, script_globals):
        PyTorchLightningScriptRunner.on_after_run(self, script_globals)

    @classmethod
    def distributions(cls):
        return None

    def add_progress_tracking(self, tracer):
        from pytorch_lightning import Trainer
        from pytorch_lightning.callbacks import Callback

        class ProgressCallback(Callback):
            def __init__(self, work):
                self.work = work

            def on_train_batch_end(self, trainer, pl_module, *_: Any) -> None:
                progress = 100 * (trainer.fit_loop.total_batch_idx + 1) / float(trainer.estimated_stepping_batches)
                if progress > 100:
                    self.work.progress = 100
                else:
                    self.work.progress = progress

        def trainer_pre_fn(trainer, *args, **kwargs):
            callbacks = kwargs.get("callbacks", [])
            callbacks.append(ProgressCallback(self))
            return {}, args, kwargs

        tracer.add_traced(Trainer, "__init__", pre_fn=trainer_pre_fn)

        return tracer


class ObjectiveLightningTrainingComponent(LightningTrainingComponent):
    def __init__(self, *args, trial_id: int, logger: str, sweep_id: str, num_nodes: int = 1, **kwargs):
        super().__init__(
            *args,
            script_runner=PyTorchLightningObjective,
            logger=logger,
            sweep_id=sweep_id,
            trial_id=trial_id,
            num_nodes=num_nodes,
            **kwargs,
        )
        self.trial_id = trial_id
        self.has_stopped = False
        self.pruned = False
        self.params = None
        self.restart_count = 0
        self.sweep_id = sweep_id
        self.reports = []
        self.has_stored = False

    def run(self, params: Optional[Dict[str, Any]] = None, restart_count: int = 0):
        self.params = params
        self.restart_count = restart_count
        super().run(params=params, restart_count=restart_count)

    @property
    def progress(self):
        return self.ws[0].progress

    @property
    def monitor(self):
        return self.ws[0].monitor

    @property
    def best_model_path(self):
        return self.ws[0].best_model_path

    @property
    def best_model_score(self):
        return self.ws[0].best_model_score

    @property
    def has_failed(self) -> bool:
        return any(w.has_failed for w in self.works())

    @property
    def status(self):
        return self.ws[0].status

    def stop(self):
        for w in self.works():
            w.stop()
        self.has_stopped = True

    @classmethod
    def distributions(cls):
        return {}
