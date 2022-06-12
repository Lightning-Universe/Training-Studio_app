from abc import ABC, abstractmethod

import optuna
from typing import Dict
from lightning.components.python import TracerPythonScript


class BaseObjectiveWork(TracerPythonScript, ABC):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, raise_exception=True, **kwargs)
        """TO BE IMPLEMENTED"""

    def run(self, trial_id: int, **params):
        """TO BE IMPLEMENTED"""

    @abstractmethod
    def distributions():
        """TO BE IMPLEMENTED"""
