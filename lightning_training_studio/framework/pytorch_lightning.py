import os
import subprocess
import sys
import time
import uuid
from typing import Any, Dict, Optional

import pytorch_lightning
from lightning.app.components.training import LightningTrainerScript, PyTorchLightningScriptRunner
from lightning.app.storage import Path

from lightning_training_studio.framework.agnostic import Objective


class PyTorchLightningObjective(Objective, PyTorchLightningScriptRunner):

    """This component executes a PyTorch Lightning script
    and injects a callback in the Trainer at runtime in order to start tensorboard server."""

    def __init__(
        self,
        *args,
        logger: str,
        sweep_id: str,
        experiment_id: int,
        experiment_name: str,
        num_nodes: int,
        last_model_path: Optional[str] = None,
        pip_install_source: bool = False,
        **kwargs,
    ):
        Objective.__init__(
            self,
            logger=logger,
            sweep_id=sweep_id,
            experiment_id=experiment_id,
            experiment_name=experiment_name,
            **kwargs,
        )
        PyTorchLightningScriptRunner.__init__(self, *args, num_nodes=num_nodes, **kwargs)
        self.progress = None
        self.total_parameters = None
        self.start_time = None
        self.end_time = None
        self.last_model_path = Path(last_model_path) if last_model_path else None
        self.pip_install_source = pip_install_source
        self._rootwd = os.getcwd()

    def configure_tracer(self):
        tracer = Objective.configure_tracer(self)
        if self.node_rank == 0:
            return self.add_metadata_tracker(tracer)
        return tracer

    def run(
        self,
        params: Optional[Dict[str, Any]] = None,
        restart_count: int = 0,
        **kwargs,
    ):
        code_dir = "."
        if self.pip_install_source:
            os.chdir(self._rootwd)
            uid = uuid.uuid4().hex[:8]
            code_dir = f"code-{uid}"
            os.makedirs(code_dir)

        if self.last_model_path:
            self.last_model_path.get(overwrite=True)
        self.params = params
        return PyTorchLightningScriptRunner.run(self, params=params, code_dir=code_dir, **kwargs)

    def on_before_run(self):
        if self.pip_install_source:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])

    def on_after_run(self, script_globals):
        self.end_time = time.time()
        self._on_after_run(script_globals)
        self.best_model_path = str(self.best_model_path)

    def _on_after_run(self, script_globals):
        for v in script_globals.values():
            if isinstance(v, (pytorch_lightning.cli.LightningCLI)):
                trainer = v.trainer
                break
            elif isinstance(v, (pytorch_lightning.Trainer)):
                trainer = v
                break
        else:
            raise RuntimeError("No trainer instance found.")

        self.monitor = trainer.checkpoint_callback.monitor

        if trainer.checkpoint_callback.best_model_score:
            self.best_model_path = Path(trainer.checkpoint_callback.best_model_path)
            self.best_model_score = float(trainer.checkpoint_callback.best_model_score)
        else:
            self.best_model_path = Path(trainer.checkpoint_callback.last_model_path)

        self.has_finished = True

    @classmethod
    def distributions(cls):
        return None

    def add_metadata_tracker(self, tracer):
        from lightning_training_studio.utilities.imports import _IS_PYTORCH_LIGHTNING_AVAILABLE

        if _IS_PYTORCH_LIGHTNING_AVAILABLE:
            import pytorch_lightning as pl
            from pytorch_lightning.callbacks import Callback
            from pytorch_lightning.strategies.deepspeed import DeepSpeedStrategy
            from pytorch_lightning.utilities import rank_zero_only
            from pytorch_lightning.utilities.model_summary.model_summary import (
                _is_lazy_weight_tensor,
                get_human_readable_count,
            )
            from pytorch_lightning.utilities.model_summary.model_summary_deepspeed import deepspeed_param_size
        else:
            import lightning.pytorch as pl
            from lightning.pytorch.callbacks import Callback
            from lightning.pytorch.strategies.deepspeed import DeepSpeedStrategy
            from lightning.pytorch.utilities import rank_zero_only
            from lightning.pytorch.utilities.model_summary.model_summary import (
                _is_lazy_weight_tensor,
                get_human_readable_count,
            )
            from lightning.pytorch.utilities.model_summary.model_summary_deepspeed import deepspeed_param_size

        class ProgressCallback(Callback):
            def __init__(self, work):
                self.work = work
                self.work.start_time = time.time()

            def setup(
                self,
                trainer,
                pl_module,
                stage: Optional[str] = None,
            ) -> None:
                trainer.checkpoint_callback.save_last = True

            @rank_zero_only
            def on_train_batch_end(self, trainer, pl_module, *args) -> None:
                progress = 100 * (trainer.fit_loop.total_batch_idx + 1) / float(trainer.estimated_stepping_batches)
                if progress > 100:
                    self.work.progress = 100
                else:
                    self.work.progress = round(progress, 4)

                if not self.work.total_parameters:
                    if isinstance(trainer.strategy, DeepSpeedStrategy) and trainer.strategy.zero_stage_3:
                        total_parameters = sum(
                            deepspeed_param_size(p) if not _is_lazy_weight_tensor(p) else 0
                            for p in pl_module.parameters()
                            if p.requires_grad
                        )
                    else:
                        total_parameters = sum(p.numel() for p in pl_module.parameters() if p.requires_grad)
                    human_readable = get_human_readable_count(total_parameters)
                    self.work.total_parameters = str(human_readable)

                if trainer.checkpoint_callback.last_model_path:
                    self.work.last_model_path = Path(trainer.checkpoint_callback.last_model_path)

        def trainer_pre_fn(trainer, *args, **kwargs):
            callbacks = kwargs.get("callbacks", [])
            callbacks.append(ProgressCallback(self))
            kwargs["callbacks"] = callbacks
            return {}, args, kwargs

        def fit_pre_fn(trainer, *args, **kwargs):
            ckpt_path = kwargs.get("ckpt_path", None)
            if not ckpt_path and isinstance(self.last_model_path, Path):
                ckpt_path = str(self.last_model_path)
                print(f"Restarting from checkpoint: {ckpt_path}")
                kwargs["ckpt_path"] = ckpt_path
            return {}, args, kwargs

        tracer.add_traced(pl.Trainer, "__init__", pre_fn=trainer_pre_fn)
        tracer.add_traced(pl.Trainer, "fit", pre_fn=fit_pre_fn)

        return tracer


class ObjectiveLightningTrainingComponent(LightningTrainerScript):
    def __init__(
        self,
        *args,
        experiment_id: int,
        experiment_name: str,
        logger: str,
        sweep_id: str,
        num_nodes: int = 1,
        pip_install_source: bool = False,
        **kwargs,
    ):
        super().__init__(
            *args,
            script_runner=PyTorchLightningObjective,
            logger=logger,
            sweep_id=sweep_id,
            experiment_id=experiment_id,
            experiment_name=experiment_name,
            num_nodes=num_nodes,
            pip_install_source=pip_install_source,
            **kwargs,
        )
        self.experiment_id = experiment_id
        self.experiment_name = experiment_name
        self.has_stopped = False
        self.pruned = False
        self.params = None
        self.restart_count = 0
        self.sweep_id = sweep_id
        self.reports = []
        self.has_stored = False

    def run(
        self, params: Optional[Dict[str, Any]] = None, restart_count: int = 0, last_model_path: Optional[str] = None
    ):
        self.params = params
        self.restart_count = restart_count
        super().run(params=params, restart_count=restart_count, last_model_path=last_model_path)

    @property
    def start_time(self):
        return self.ws[0].start_time

    @property
    def end_time(self):
        return self.ws[0].end_time

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
    def last_model_path(self):
        return self.ws[0].last_model_path

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
