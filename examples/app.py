from pathlib import Path
import optuna
from lightning import LightningFlow, CloudCompute, LightningApp
from lightning_hpo import AbstractObjectiveWork, OptunaPythonScript
from lightning.storage.path import Path

class MyCustomObjective(AbstractObjectiveWork):

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
        self.optuna_hpo = OptunaPythonScript(
            script_path=str(Path(__file__).parent / "scripts/train.py"),
            total_trials=4,
            simultaneous_trials=2,
            objective_work_cls=MyCustomObjective,
            script_args=[
                "--trainer.max_epochs=5",
                "--trainer.limit_train_batches=4",
                "--trainer.limit_val_batches=4",
                "--trainer.callbacks=ModelCheckpoint",
                "--trainer.callbacks.monitor=val_acc",
            ],
            cloud_compute=CloudCompute("cpu", 1),
            objective_work_kwargs={"raise_exception": True},
        )

    def run(self):
        self.optuna_hpo.run()

        if self.optuna_hpo.best_model_path:
            pass

    def configure_layout(self):
        return [{"name": "HiPlot", "content": self.optuna_hpo.hi_plot}]

app = LightningApp(RootFlow())