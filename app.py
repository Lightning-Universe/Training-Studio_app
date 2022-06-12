from pathlib import Path
import optuna
from lightning import LightningFlow, CloudCompute, LightningApp
from lightning_hpo import BaseObjectiveWork, OptunaPythonScript
from lightning.storage.path import Path

class MyCustomObjective(BaseObjectiveWork):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        """TO BE IMPLEMENTED"""

    def on_after_run(self, res):
        """TO BE IMPLEMENTED"""

    @staticmethod
    def distributions():
        """TO BE IMPLEMENTED"""


class RootFlow(LightningFlow):

    def __init__(self):
        super().__init__()
        self.hpo_train = OptunaPythonScript(
            script_path=str(Path(__file__).parent / "scripts/train.py"),
            total_trials=50,
            simultaneous_trials=2,
            objective_work_cls=BaseObjectiveWork,
            script_args=[
                "--trainer.max_epochs=5",
                "--trainer.limit_train_batches=4",
                "--trainer.limit_val_batches=4",
                "--trainer.callbacks=ModelCheckpoint",
                "--trainer.callbacks.monitor=val_acc",
            ],
            cloud_compute=CloudCompute("cpu"),
        )

    def run(self):
        self.hpo_train.run()

        if self.hpo_train.best_model_path:
            pass

    def configure_layout(self):
        return [{"name": "HiPlot", "content": self.hpo_train.hi_plot}]

app = LightningApp(RootFlow())