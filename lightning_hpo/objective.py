from abc import ABC, abstractmethod
from functools import partial
import optuna
from typing import Dict, Any
from lightning.app.components.python import TracerPythonScript
from lightning_hpo.loggers import Loggers
import os

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
        tracer = super().configure_tracer()
        if self.logger == Loggers.STREAMLIT:
            return tracer

        from pytorch_lightning import Trainer
        from pytorch_lightning.loggers import WandbLogger
        import wandb

        wandb.init(
            project=self.sweep_id,
            entity=os.getenv('WANDB_ENTITY'),
            name=f"trial_{self.trial_id}",
            config=self.params
        )

        def trainer_pre_fn(self, *args, work=None, **kwargs):
            logger = WandbLogger(
                save_dir=os.path.dirname(__file__),
                project=work.sweep_id,
                entity=os.getenv('WANDB_ENTITY'),
                name=f"trial_{work.trial_id}",
            )
            kwargs['logger'] = [logger]
            return {}, args, kwargs

        tracer = super().configure_tracer()
        tracer.add_traced(Trainer, "__init__", pre_fn=partial(trainer_pre_fn, work=self))
        return tracer

    def run(self, params: Dict[str, Any]):
        self.params = params
        self.script_args.extend([f"--{k}={v}" for k, v in params.items()])
        return super().run()

    @abstractmethod
    def distributions() -> Dict[str,  optuna.distributions.BaseDistribution]:
        pass