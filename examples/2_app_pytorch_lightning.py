import os.path as ops

from lightning import LightningApp

from lightning_hpo import CloudCompute, Sweep
from lightning_hpo.algorithm.optuna import OptunaAlgorithm
from lightning_hpo.distributions.distributions import Categorical, IntUniform, LogUniform, Uniform

app = LightningApp(
    Sweep(
        script_path=ops.join(ops.dirname(__file__), "scripts/train.py"),
        n_trials=5,
        simultaneous_trials=1,
        distributions={
            "model.lr": LogUniform(0.001, 0.1),
            "model.gamma": Uniform(0.5, 0.8),
            "data.batch_size": Categorical([16, 32, 64]),
            "trainer.max_epochs": IntUniform(3, 15),
        },
        algorithm=OptunaAlgorithm(direction="maximize"),
        cloud_compute=CloudCompute("gpu-fast-multi", count=1),  # 2 * 4 V100
        framework="pytorch_lightning",
        logger="tensorboard",
        sweep_id="Optimizing a Simple CNN over MNIST with Lightning HPO",
    )
)
