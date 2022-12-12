from unittest.mock import MagicMock

from lightning_training_studio.commands.tensorboard.stop import TensorboardConfig
from lightning_training_studio.controllers import controller, tensorboard
from lightning_training_studio.controllers.tensorboard import TensorboardController
from lightning_training_studio.utilities.enum import Stage
from tests.helpers import MockDatabaseClient


def test_tensorboard_controller(monkeypatch):

    tensorboard_controller = TensorboardController()
    monkeypatch.setattr(controller, "DatabaseClient", MockDatabaseClient)
    run = MagicMock()
    stop = MagicMock()
    monkeypatch.setattr(tensorboard.Tensorboard, "run", run)
    monkeypatch.setattr(tensorboard.Tensorboard, "stop", stop)
    monkeypatch.setattr(tensorboard.Tensorboard, "_check_run_is_implemented", lambda x: None)
    tensorboard_controller.run("a", "b")
    assert tensorboard_controller.db.data == {}

    config = TensorboardConfig(id=1, sweep_id="a", shared_folder="s")
    response = tensorboard_controller.run_tensorboard(config)
    assert response == "Launched a Tensorboard `a`."
    assert len(tensorboard_controller.db.data) == 1
    config: TensorboardConfig = tensorboard_controller.db.select_all()[0]
    assert config.stage == Stage.NOT_STARTED
    assert config.desired_stage == Stage.RUNNING

    run.assert_not_called()
    tensorboard_controller.run("a", "b")
    run.assert_called()
    tensorboard_obj_1 = tensorboard_controller.r["a"]
    assert isinstance(tensorboard_obj_1, tensorboard.Tensorboard)
    assert tensorboard_obj_1.collect_model() != config
    assert tensorboard_obj_1.collect_model().stage == Stage.PENDING

    tensorboard_obj_1._url = "abc"
    tensorboard_controller.run("a", "b")
    assert tensorboard_obj_1.stage == Stage.PENDING

    stop.assert_not_called()
    response = tensorboard_controller.stop_tensorboard(config)
    stop.assert_called()
    assert response == "Tensorboard `a` was stopped."
    assert tensorboard_controller.r == {}
    config = tensorboard_controller.db.select_all()[0]
    assert config.stage == Stage.STOPPED
    assert config.desired_stage == Stage.STOPPED

    response = tensorboard_controller.run_tensorboard(config)
    config = tensorboard_controller.db.select_all()[0]
    assert config.stage == Stage.STOPPED
    assert config.desired_stage == Stage.RUNNING
    assert response == "Re-Launched a Tensorboard `a`."
    tensorboard_controller.run("a", "b")
    assert isinstance(tensorboard_controller.r["a"], tensorboard.Tensorboard)
    assert tensorboard_controller.r["a"] != tensorboard_obj_1
