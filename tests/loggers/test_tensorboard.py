from unittest.mock import MagicMock


def test_tensorboard_logger(monkeypatch):

    from lightning_training_studio.loggers import tensorboard

    pytorch_lightning = MagicMock()
    monkeypatch.setattr(tensorboard, "pytorch_lightning", pytorch_lightning)
    logger = tensorboard.TensorboardLogger()

    def add_traced(cls, name, pre_fn=None):
        setattr(cls, "v" + name, pre_fn)

    tracer = MagicMock()
    tracer.add_traced = add_traced
    logger.configure_tracer(tracer, "a", 0, "a", {"x": 1})
    _, _, kwargs = pytorch_lightning.Trainer.v__init__(MagicMock, (), {})
    assert kwargs["logger"].__class__.__name__ == "TensorBoardLogger"
