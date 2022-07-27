import os

import optuna
from lightning import CloudCompute, LightningApp, LightningFlow
from lightning.app.storage.path import Path
from lightning_hpo import BaseObjective, Optimizer

class MyCustomObjective(BaseObjective):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.best_model_path = None

    def on_after_run(self, res):
        self.best_model_score = float(res["cli"].trainer.checkpoint_callback.best_model_score)
        self.best_model_path = Path(res["cli"].trainer.checkpoint_callback.best_model_path)

    @staticmethod
    def distributions():
        return {"model.lr": optuna.distributions.LogUniformDistribution(0.0001, 0.1)}


class RootFlow(LightningFlow):
    def __init__(self):
        super().__init__()
        self.hpo_train = Optimizer(
            script_path=str(Path(__file__).parent / "scripts/train.py"),
            n_trials=5,
            simultaneous_trials=2,
            objective_cls=MyCustomObjective,
            script_args=[
                "--trainer.max_epochs=5",
                "--trainer.limit_train_batches=4",
                "--trainer.limit_val_batches=4",
                "--trainer.callbacks=ModelCheckpoint",
                "--trainer.callbacks.monitor=val_acc",
            ],
            cloud_compute=CloudCompute("default"),
            logger=os.environ.get("LOGGER", "streamlit"),
            sweep_id=os.environ.get("PROJECT"),
        )

    def run(self):
        self.hpo_train.run()

    def configure_layout(self):
        return self.hpo_train.configure_layout()


app = LightningApp(RootFlow())
