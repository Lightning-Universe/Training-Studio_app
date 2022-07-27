import os
from abc import ABC, abstractmethod
from functools import partial
from typing import Any, Dict

import optuna
from lightning.app.components.python import TracerPythonScript

from lightning_hpo.loggers import LoggerType


class BaseObjective(TracerPythonScript, ABC):
    def __init__(self, *args, logger: str, sweep_id: str, trial_id, **kwargs):
        super().__init__(*args, raise_exception=True, **kwargs)
        self.trial_id = trial_id
        self.best_model_score = None
        self.params = None
        self.has_told_study = False
        self.reports = []
        self.flow_reports = []
        self.pruned = False
        self.logger = logger
        self._url = None
        self.sweep_id = sweep_id

    def configure_tracer(self):
        assert self.params
        tracer = super().configure_tracer()

        from pytorch_lightning import Trainer
        from pytorch_lightning.loggers import WandbLogger

        import wandb

        wandb.init(
            project=self.sweep_id,
            entity=os.getenv("WANDB_ENTITY"),
            name=f"trial_{self.trial_id}",
            config=self.params,
        )

        def trainer_pre_fn(trainer, *args, **kwargs):
            raise Exception("HERE")
            logger = WandbLogger(
                save_dir=os.path.join(os.getcwd(), os.environ.get("LOGS_DIR")),
                project=self.sweep_id,
                entity=os.getenv("WANDB_ENTITY"),
                name=f"trial_{self.trial_id}",
            )
            kwargs["logger"] = [logger]
            return {}, args, kwargs

        tracer.add_traced(Trainer, "__init__", trainer_pre_fn)

        # LoggerType(self.logger).get_logger().configure_tracer(
        #     tracer,
        #     params=self.params,
        #     trial_id=self.trial_id
        # )
        return tracer

    def run(self, params: Dict[str, Any]):
        self.params = params
        return super().run(params=params)

    @abstractmethod
    def distributions() -> Dict[str, optuna.distributions.BaseDistribution]:
        pass
