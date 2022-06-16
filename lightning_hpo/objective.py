from abc import ABC, abstractmethod
from typing import Dict, Any
from lightning.app.components.python import TracerPythonScript


class BaseObjectiveWork(TracerPythonScript, ABC):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, raise_exception=True, **kwargs)
        self.trial_id = None
        self.params = None
        self.best_model_score = None
        self.best_model_path = None

    def run(self, trial_id: int, params: Dict[str, Any]):
        self.trial_id = trial_id
        self.params = params
        self.script_args += [f"--{k}={v}" for k, v in params.items()]
        super().run()

    @abstractmethod
    def distributions():
        pass
