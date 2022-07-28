import optuna
from lightning import CloudCompute, LightningApp
from lightning.app.storage.path import Path

from lightning_hpo import BaseObjective, Optimizer


class MyCustomObjective(BaseObjective):
    def on_after_run(self, script_globals):
        # Collect metadata directly from the script.
        self.best_model_path = Path(script_globals["cli"].trainer.checkpoint_callback.best_model_path)
        self.best_model_score = float(script_globals["cli"].trainer.checkpoint_callback.best_model_score)
        self.monitor = script_globals["cli"].trainer.checkpoint_callback.monitor

    @staticmethod
    def distributions():
        return {"model.lr": optuna.distributions.LogUniformDistribution(0.0001, 0.1)}


app = LightningApp(
    Optimizer(
        script_path=str(Path(__file__).parent / "scripts/train.py"),
        n_trials=5,
        simultaneous_trials=1,
        objective_cls=MyCustomObjective,
        script_args=[
            "--trainer.max_epochs=5",
            "--trainer.callbacks=ModelCheckpoint",
            "--trainer.callbacks.monitor=val_acc",
            "--trainer.limit_train_batches=20",
            "--trainer.limit_val_batches=5",
        ],
        cloud_compute=CloudCompute("default"),
        logger="wandb",
        study=optuna.create_study(direction="maximize"),
    )
)
