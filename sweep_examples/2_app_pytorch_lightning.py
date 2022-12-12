import os.path as ops

import optuna
from lightning import LightningApp

from lightning_training_studio import Sweep
from lightning_training_studio.algorithm.optuna import OptunaAlgorithm
from lightning_training_studio.distributions.distributions import Categorical, IntUniform, LogUniform, Uniform

app = LightningApp(
    Sweep(
        script_path=ops.join(ops.dirname(__file__), "scripts/train.py"),
        total_experiments=3,
        parallel_experiments=1,
        distributions={
            "--model.lr": LogUniform(0.001, 0.1),
            "--model.gamma": Uniform(0.5, 0.8),
            "--data.batch_size": Categorical([16, 32, 64]),
            "--trainer.max_epochs": IntUniform(1, 5),
        },
        algorithm=OptunaAlgorithm(optuna.create_study(direction="maximize")),
        framework="pytorch_lightning",
    )
)
