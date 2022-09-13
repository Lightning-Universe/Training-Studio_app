from unittest.mock import MagicMock

import pytest
from lightning.app.storage import Drive

from lightning_hpo.commands.tensorboard.stop import TensorboardConfig
from lightning_hpo.components import tensorboard as T


def test_tensorboard_work(monkeypatch):
    def fn(*_):
        raise Exception("HERE")

    monkeypatch.setattr(T, "Popen", MagicMock())
    monkeypatch.setattr(T, "sleep", fn)

    config = TensorboardConfig(id=0, sweep_id="1", shared_folder="")
    drive = Drive("lit://a")
    tensorboard = T.Tensorboard(drive=drive, config=config)
    with pytest.raises(Exception, match="HERE"):
        tensorboard.run()
