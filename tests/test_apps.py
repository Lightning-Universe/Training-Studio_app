import os
from functools import partial
from unittest import mock

import pytest
from lightning.app.testing import application_testing, LightningTestApp


class LightningHPOTestApp(LightningTestApp):
    def __init__(self, root, n_trials=4, simultaneous_trials=2, **kwargs):
        root.n_trials = n_trials
        root.num_trials = root.simultaneous_trials = simultaneous_trials
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


@pytest.mark.skip(reason="TODO: See if this test is still relevant")
@mock.patch.dict(os.environ, {"WANDB_ENTITY": "thomas-chaton"})
@mock.patch.dict(os.environ, {"WANDB_API_KEY": "eabe6ced59f74db139187745544572f81ef76162"})
def test_custom_objective_sweep_streamlit():

    command_line = [
        os.path.join(os.getcwd(), "examples/1_app_agnostic.py"),
        "--open-ui",
        "False",
    ]
    result = application_testing(LightningHPOTestApp, command_line)
    assert result.exit_code == 0, result.__dict__


@mock.patch.dict(os.environ, {"WANDB_ENTITY": "thomas-chaton"})
@mock.patch.dict(os.environ, {"WANDB_API_KEY": "eabe6ced59f74db139187745544572f81ef76162"})
def test_pytorch_lightning_objective_sweep_wandb():

    command_line = [
        os.path.join(os.getcwd(), "examples/2_app_pytorch_lightning.py"),
        "--open-ui",
        "False",
    ]
    result = application_testing(partial(LightningHPOTestApp, n_trials=1, simultaneous_trials=1), command_line)
    assert result.exit_code == 0, result.__dict__
