from typing import Any, Dict

import optuna

from lightning_training_studio.algorithm import OptunaAlgorithm
from lightning_training_studio.components.sweep import Sweep
from lightning_training_studio.distributions import Categorical, Uniform
from lightning_training_studio.utilities.enum import Stage
from tests.helpers import FailedMockObjective, MockObjective


def test_sweep_with_failed_experiments():

    sweep = Sweep(
        5,
        parallel_experiments=3,
        objective_cls=FailedMockObjective,
        distributions={
            "best_model_score": Uniform(0, 100),
            "best_model_path": Categorical(choices=["a", "b", "c", "d", "e", "f", "g"]),
        },
    )

    sweep.run()
    assert sweep.stage == Stage.FAILED
    assert sweep.experiments[0]["exception"] == "Error"
    assert sweep.experiments[0]["stage"] == "failed"


class PrunedMockObjective(MockObjective):
    def run(self, params: Dict[str, Any], restart_count: int):
        super().run(params, restart_count)
        score = params["best_model_score"]
        score = score + 1 if score > 5 else 1
        self.reports = [(score, idx) for idx in range(100)]


def test_sweep_pruned():

    sweep = Sweep(
        total_experiments=25,
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
        assert len(sweep.experiments) == idx
        sweep.run()

    assert sweep.total_experiments == 25
    sweep.run()
    assert sweep.total_experiments == 25
    assert "pruned" in {v["stage"] for k, v in sweep.experiments.items()}
