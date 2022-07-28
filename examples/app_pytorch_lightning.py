import optuna
from lightning import CloudCompute, LightningApp
from lightning.app.storage.path import Path

from lightning_hpo import Optimizer

app = LightningApp(
    Optimizer(
        script_path=str(Path(__file__).parent / "scripts/train.py"),
        n_trials=5,
        simultaneous_trials=1,
        distributions={
            "model.lr": optuna.distributions.LogUniformDistribution(0.001, 0.1),
            "model.gamma": optuna.distributions.UniformDistribution(0.5, 0.8),
            "data.batch_size": optuna.distributions.CategoricalDistribution([16, 32, 64]),
            "trainer.max_epochs": optuna.distributions.IntUniformDistribution(3, 15),
        },
        cloud_compute=CloudCompute("default"),
        framework="pytorch_lightning",
        logger="wandb",
        study=optuna.create_study(direction="maximize"),
        num_nodes=2,
    )
)
