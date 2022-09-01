import numpy as np

from lightning_hpo.components.sweep import Sweep
from lightning_hpo.framework.agnostic import BaseObjective


class Custom(BaseObjective):
    def objective(self, *args, **kwargs):
        self.best_model_score = np.random.randint(-10, 10)


def test_sweep_database_interraction():
    Sweep(script_path=__file__, n_trials=5, simultaneous_trials=1)
