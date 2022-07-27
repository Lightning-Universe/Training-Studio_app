from lightning.app.testing import LightningTestApp, application_testing
from lightning.app.cli.lightning_cli import run
import os
from unittest import mock

class LightningHPOTestApp(LightningTestApp):

    def __init__(self, root, **kwargs):
        root.n_trials = 4
        root.num_trials = root.simultaneous_trials = 2
        script_args = [
            "--trainer.max_epochs=5",
            "--trainer.limit_train_batches=1",
            "--trainer.limit_val_batches=1",
            "--trainer.callbacks=ModelCheckpoint",
            "--trainer.callbacks.monitor=val_acc",
        ]
        for idx in range(root.n_trials):
            getattr(root, f"w_{idx}").script_args = script_args
        super().__init__(root, **kwargs)

    def on_before_run_once(self):
        if self.root.num_trials > self.root.n_trials:
            return True


@mock.patch.dict(os.environ, {"WANDB_ENTITY": "thomas-chaton"})
@mock.patch.dict(os.environ, {"WANDB_API_KEY": "eabe6ced59f74db139187745544572f81ef76162"})
def test_custom_objective_optimizer_wandb():

    command_line = [
        os.path.join(os.getcwd(), "app.py"),
        "--open-ui",
        "False",
    ]
    result = application_testing(LightningHPOTestApp, command_line)
    assert result.exit_code == 0, result.__dict__