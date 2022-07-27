import optuna
from lightning import CloudCompute, LightningApp
from lightning.app.storage.path import Path

from lightning_hpo import Optimizer

app = LightningApp(
    Optimizer(
        script_path=str(Path(__file__).parent / "scripts/train.py"),
        n_trials=5,
        simultaneous_trials=1,
        distributions={"model.lr": optuna.distributions.LogUniformDistribution(0.0001, 0.1)},
        framework="pytorch_lightning",
        script_args=[
            "--trainer.max_epochs=5",
            "--trainer.callbacks=ModelCheckpoint",
            "--trainer.callbacks.monitor=val_acc",
            "--trainer.limit_train_batches=5",
            "--trainer.limit_val_batches=5",
        ],
        cloud_compute=CloudCompute("default"),
        logger="wandb",
    )
)
