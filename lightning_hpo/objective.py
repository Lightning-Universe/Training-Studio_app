import os
from abc import ABC, abstractmethod

import optuna
from typing import Dict
from lightning.components.python import TracerPythonScript


class AbstractObjectiveWork(TracerPythonScript, ABC):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trial_id = None
        self.best_model_score = None
        self.params = None
        self.has_told_study = False

    def run(self, trial_id: int, **params):
        self.trial_id = trial_id
        self.params = params
        self.script_args.extend([f"--{k}={v}" for k, v in params.items()])
        return super().run()

    @abstractmethod
    def distributions() -> Dict[str,  optuna.distributions.BaseDistribution]:
        pass
