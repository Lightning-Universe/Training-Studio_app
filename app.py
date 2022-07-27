from optuna.distributions import LogUniformDistribution
from lightning import LightningFlow, CloudCompute, LightningApp
from lightning_hpo import Optimizer

class RootFlow(LightningFlow):

    def __init__(self):
        super().__init__()
        self.hpo_train = Optimizer(
            script_path="train.py",
            n_trials=100,
            simultaneous_trials=10,
            script_args=[
                "--trainer.max_epochs=100",
                "--trainer.callbacks=ModelCheckpoint",
                "--trainer.callbacks.monitor=val_acc",
            ],
            cloud_compute=CloudCompute("gpu"),
            distributions={"--model.lr": LogUniformDistribution(0.1, 1)},
            logger="wandb",
            framework="pytorch_lightning"
        )

    def run(self):
        self.hpo_train.run()

        if self.hpo_train.best_model_path:
            pass

    def configure_layout(self):
        return self.hpo_train.configure_layout()

app = LightningApp(RootFlow())
