from typing import Any, Dict

import optuna

from lightning_hpo.algorithm import OptunaAlgorithm
from lightning_hpo.components.sweep import Sweep
from lightning_hpo.distributions import Categorical, Uniform
from lightning_hpo.utilities.enum import Stage
from tests.helpers import FailedMockObjective, MockObjective


def test_sweep_with_failed_trials():

    sweep = Sweep(
        5,
        simultaneous_trials=3,
        objective_cls=FailedMockObjective,
        distributions={
            "best_model_score": Uniform(0, 100),
            "best_model_path": Categorical(choices=["a", "b", "c", "d", "e", "f", "g"]),
        },
    )

    sweep.run()
    assert sweep.stage == Stage.FAILED
    assert sweep.trials[0]["exception"] == "Error"


class PrunedMockObjective(MockObjective):
    def run(self, params: Dict[str, Any], restart_count: int):
        super().run(params, restart_count)
        score = params["best_model_score"]
        score = score + 1 if score > 5 else 1
        self.reports = [(score, idx) for idx in range(100)]


def test_sweep_pruned():

    sweep = Sweep(
        n_trials=25,
        objective_cls=PrunedMockObjective,
        distributions={
            "best_model_score": Uniform(0, 10),
        },
        algorithm=OptunaAlgorithm(
            optuna.create_study(
                pruner=optuna.pruners.MedianPruner(),
                direction="maximize",
            )
        ),
    )

    for idx in range(25):
        assert len(sweep.trials) == idx
        sweep.run()

    assert sweep.n_trials == 25
    sweep.run()
    assert sweep.n_trials == 25
    assert "pruned" in {v["stage"] for k, v in sweep.trials.items()}