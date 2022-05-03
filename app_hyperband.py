from pathlib import Path
import optuna
import os
from functools import partial
from lightning import LightningFlow, CloudCompute, LightningApp
from lightning_hpo import AbstractObjectiveWork, OptunaPythonScript
from lightning.storage.path import Path

class MyCustomObjective(AbstractObjectiveWork):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.best_model_path = None

    def configure_tracer(self):
        from pytorch_lightning import Trainer
        from pytorch_lightning.callbacks import Callback
        from pytorch_lightning.loggers import WandbLogger

        tracer = super().configure_tracer()

        class WorkCollector(Callback):

            def __init__(self, work):
                self._work = work

            def on_validation_epoch_end(self, trainer, *_):
                if trainer.checkpoint_callback.best_model_score:
                    report = [(float(trainer.checkpoint_callback.best_model_score), trainer.global_step)]
                    self._work.reports = self._work.reports + report

        def trainer_pre_fn(self, *args, work=None, **kwargs):
            # Dynamically inject the callback inside the Trainer.
            kwargs['callbacks'].append(WorkCollector(work))
            return {}, args, kwargs

        tracer = super().configure_tracer()
        tracer.add_traced(Trainer, "__init__", pre_fn=partial(trainer_pre_fn, work=self))
        return tracer

    def on_after_run(self, res):
        self.best_model_score = float(res["cli"].trainer.checkpoint_callback.best_model_score)
        self.best_model_path = Path(res["cli"].trainer.checkpoint_callback.best_model_path)

    @staticmethod
    def distributions():
        return {"model.lr": optuna.distributions.LogUniformDistribution(0.0001, 0.1)}


class RootFlow(LightningFlow):

    def __init__(self):
        super().__init__()
        self.hpo_train = OptunaPythonScript(
            script_path=str(Path(__file__).parent / "scripts/train.py"),
            total_trials=2,
            simultaneous_trials=1,
            study = optuna.create_study(
                direction="maximize",
                pruner=optuna.pruners.HyperbandPruner(
                    min_resource=1, max_resource=10, reduction_factor=3
                ),
            ),
            objective_work_cls=MyCustomObjective,
            script_args=[
                "--trainer.max_epochs=10",
                "--trainer.limit_train_batches=4",
                "--trainer.limit_val_batches=4",
                "--trainer.callbacks=ModelCheckpoint",
                "--trainer.callbacks.monitor=val_acc",
            ],
            cloud_compute=CloudCompute("cpu", 1, idle_timeout=0 # kill as soon as successfull.)
        )

    def run(self):
        self.hpo_train.run()

        if self.hpo_train.best_model_path:
            pass

    def configure_layout(self):
        return [{"name": "HiPlot", "content": self.hpo_train.hi_plot}]

app = LightningApp(RootFlow())