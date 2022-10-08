from datetime import datetime
from typing import Any, Dict, Optional

from lightning.app.components.python import TracerPythonScript
from lightning.app.components.training import LightningTrainingComponent, PyTorchLightningScriptRunner
from lightning.pytorch.utilities.model_summary import get_human_readable_count

from lightning_hpo.framework.agnostic import Objective


class PyTorchLightningObjective(Objective, PyTorchLightningScriptRunner):

    """This component executes a PyTorch Lightning script
    and injects a callback in the Trainer at runtime in order to start tensorboard server."""

    def __init__(self, *args, logger: str, sweep_id: str, trial_id: int, num_nodes: int, **kwargs):
        Objective.__init__(self, logger=logger, sweep_id=sweep_id, trial_id=trial_id, **kwargs)
        PyTorchLightningScriptRunner.__init__(self, *args, num_nodes=num_nodes, **kwargs)
        self.progress = None
        self.total_parameters = None
        self.start_time = None

    def configure_tracer(self):
        if self.node_rank == 0:
            tracer = Objective.configure_tracer(self)
            return self.add_metadata_tracker(tracer)
        return TracerPythonScript.configure_tracer(self)

    def run(self, params: Optional[Dict[str, Any]] = None, restart_count: int = 0, **kwargs):
        self.params = params
        return PyTorchLightningScriptRunner.run(self, params=params, **kwargs)

    def on_after_run(self, script_globals):
        PyTorchLightningScriptRunner.on_after_run(self, script_globals)
        self.best_model_path = str(self.best_model_path)

    @classmethod
    def distributions(cls):
        return None

    def add_metadata_tracker(self, tracer):
        import time

        import psutil
        import pytorch_lightning as pl
        import torch
        from lightning_utilities.core.rank_zero import rank_zero_info
        from pytorch_lightning.callbacks import Callback

        class CUDACallback(Callback):
            def on_train_epoch_start(self, trainer, pl_module):
                # Reset the memory use counter
                torch.cuda.reset_peak_memory_stats(trainer.root_gpu)
                torch.cuda.synchronize(trainer.root_gpu)
                self.start_time = time.time()

            def on_batch_end(self, trainer, pl_module) -> None:
                torch.cuda.synchronize(trainer.root_gpu)
                max_memory = torch.cuda.max_memory_allocated(trainer.root_gpu) / 2**20

                virt_mem = psutil.virtual_memory()
                virt_mem = round((virt_mem.used / (1024**3)), 2)
                pl_module.log("Peak CUDA Memory (GiB)", max_memory / 1000, prog_bar=True, on_step=True, sync_dist=True)
                pl_module.log("Average Virtual memory (GiB)", virt_mem, prog_bar=True, on_step=True, sync_dist=True)

            def on_train_epoch_end(self, trainer, pl_module):
                torch.cuda.synchronize(trainer.root_gpu)
                max_memory = torch.cuda.max_memory_allocated(trainer.root_gpu) / 2**20
                epoch_time = time.time() - self.start_time
                virt_mem = psutil.virtual_memory()
                virt_mem = round((virt_mem.used / (1024**3)), 2)
                swap = psutil.swap_memory()
                swap = round((swap.used / (1024**3)), 2)

                max_memory = trainer.training_type_plugin.reduce(max_memory)
                epoch_time = trainer.training_type_plugin.reduce(epoch_time)
                virt_mem = trainer.training_type_plugin.reduce(virt_mem)
                swap = trainer.training_type_plugin.reduce(swap)

                rank_zero_info(f"Average Epoch time: {epoch_time:.2f} seconds")
                rank_zero_info(f"Average Peak CUDA memory {max_memory:.2f} MiB")
                rank_zero_info(f"Average Peak Virtual memory {virt_mem:.2f} GiB")
                rank_zero_info(f"Average Peak Swap memory {swap:.2f} Gib")

        class ProgressCallback(Callback):
            def __init__(self, work):
                self.work = work
                self.work.start_time = str(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))

            def on_train_batch_end(self, trainer, pl_module, *_: Any) -> None:
                progress = 100 * (trainer.fit_loop.total_batch_idx + 1) / float(trainer.estimated_stepping_batches)
                if progress > 100:
                    self.work.progress = 100
                else:
                    self.work.progress = round(progress, 4)

                if not self.work.total_parameters:
                    total_parameters = sum(p.numel() for p in pl_module.parameters())
                    human_readable = get_human_readable_count(total_parameters)
                    self.work.total_parameters = human_readable

                if trainer.checkpoint_callback.best_model_score:
                    self.best_model_score = float(trainer.checkpoint_callback.best_model_score)

        def trainer_pre_fn(trainer, *args, **kwargs):
            callbacks = kwargs.get("callbacks", [])
            callbacks.append(ProgressCallback(self))
            kwargs["callbacks"] = callbacks
            return {}, args, kwargs

        tracer.add_traced(pl.Trainer, "__init__", pre_fn=trainer_pre_fn)

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
    def start_time(self):
        return self.ws[0].start_time

    @property
    def total_parameters(self):
        return self.ws[0].total_parameters

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
