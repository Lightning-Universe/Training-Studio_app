import os
from unittest.mock import MagicMock

import pytest

from lightning_training_studio.loggers import wandb as wandb_logger


def test_wandb_logger(monkeypatch):

    wandb = MagicMock()
    pytorch_lightning = MagicMock()
    api = MagicMock()
    report = MagicMock()
    report.id = "c"
    api.create_report.return_value = report
    wandb.Api.return_value = api

    monkeypatch.setattr(wandb_logger, "wandb", wandb)
    monkeypatch.setattr(wandb_logger, "pytorch_lightning", pytorch_lightning)

    with pytest.raises(Exception, match="setting your API key or entity"):
        logger = wandb_logger.WandbLogger()

    monkeypatch.setattr(os, "environ", {"WANDB_API_KEY": "a", "WANDB_ENTITY": "b"})
    logger = wandb_logger.WandbLogger()
    logger.on_after_experiment_start("a")
    assert report.title == "A Report"
    assert logger.report_url == "https://wandb.ai/b/a/reports/a--c"

    report.save.assert_called()
    logger.report.blocks = None
    logger.on_after_experiment_end("a", 0, "val_acc", 1, {"x": 1})
    assert logger.report.blocks

    assert logger.configure_layout() == [
        {"name": "Project", "content": "https://wandb.ai/b/a/reports/a"},
        {"name": "Report", "content": "https://wandb.ai/b/a/reports/a--c"},
    ]
    logger.connect(MagicMock())
    assert logger.get_url(0) == "https://wandb.ai/b/a/reports/a--c"

    def add_traced(cls, name, pre_fn=None):
        setattr(cls, "v" + name, pre_fn)

    tracer = MagicMock()
    tracer.add_traced = add_traced
    logger.configure_tracer(tracer, "a", 0, "a", {"x": 1})
    assert pytorch_lightning.Trainer.v__init__.__name__ == "trainer_pre_fn"
