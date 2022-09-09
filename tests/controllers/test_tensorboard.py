from unittest.mock import MagicMock

from lightning_hpo.commands.tensorboard.stop import TensorboardConfig
from lightning_hpo.controllers import controller, tensorboard
from lightning_hpo.controllers.tensorboard import TensorboardController
from lightning_hpo.utilities.enum import Status
from tests.helpers import MockDatabaseConnector


def test_tensorboard_controller(monkeypatch):

    tensorboard_controller = TensorboardController()
    monkeypatch.setattr(controller, "DatabaseConnector", MockDatabaseConnector)
    run = MagicMock()
    stop = MagicMock()
    monkeypatch.setattr(tensorboard.Tensorboard, "run", run)
    monkeypatch.setattr(tensorboard.Tensorboard, "stop", stop)
    tensorboard_controller.run("a")
    assert tensorboard_controller.db.data == {}

    config = TensorboardConfig(id=1, sweep_id="a", shared_folder="s")
    response = tensorboard_controller.run_tensorboard(config)
    assert response == "Launched a Tensorboard `a`."
    assert len(tensorboard_controller.db.data) == 1
    config = tensorboard_controller.db.get()[0]
    assert config.status == Status.NOT_STARTED
    assert config.desired_state == Status.RUNNING

    run.assert_not_called()
    tensorboard_controller.run("a")
    run.assert_called()
    tensorboard_obj_1 = tensorboard_controller.r["a"]
    assert isinstance(tensorboard_obj_1, tensorboard.Tensorboard)
    assert tensorboard_obj_1._config == config

    tensorboard_obj_1._url = "abc"
    tensorboard_obj_1.has_updated = True

    tensorboard_controller.run("a")
    assert tensorboard_obj_1._config.status == Status.RUNNING

    stop.assert_not_called()
    response = tensorboard_controller.stop_tensorboard(config)
    stop.assert_called()
    assert response == "Tensorboard `a` was stopped."
    assert tensorboard_controller.r == {}
    config = tensorboard_controller.db.get()[0]
    assert config.status == Status.STOPPED
    assert config.desired_state == Status.STOPPED

    response = tensorboard_controller.run_tensorboard(config)
    config = tensorboard_controller.db.get()[0]
    assert config.status == Status.STOPPED
    assert config.desired_state == Status.RUNNING
    assert response == "Re-Launched a Tensorboard `a`."
    tensorboard_controller.run("a")
    assert isinstance(tensorboard_controller.r["a"], tensorboard.Tensorboard)
    assert tensorboard_controller.r["a"] != tensorboard_obj_1
