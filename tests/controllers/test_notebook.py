from unittest.mock import MagicMock

import pytest
from lightning.app.utilities.enum import CacheCallsKeys

from lightning_training_studio.commands.notebook.run import NotebookConfig
from lightning_training_studio.controllers import controller, notebook
from lightning_training_studio.controllers.notebook import NotebookController
from lightning_training_studio.utilities.enum import Stage
from tests.helpers import MockDatabaseClient


@pytest.mark.skipif(True, reason="Seems to be hanging in the CI")
def test_notebook_controller(monkeypatch):
    notebook_controller = NotebookController()
    monkeypatch.setattr(controller, "DatabaseClient", MockDatabaseClient)
    run = MagicMock()
    stop = MagicMock()
    monkeypatch.setattr(notebook.JupyterLab, "run", run)
    monkeypatch.setattr(notebook.JupyterLab, "stop", stop)
    monkeypatch.setattr(notebook.JupyterLab, "_check_run_is_implemented", lambda x: None)
    notebook_controller.run("a", "token")
    assert notebook_controller.db.data == {}

    config = NotebookConfig(notebook_name="a", requirements=[], cloud_compute="cpu")
    response = notebook_controller.run_notebook(config)
    assert response == "The notebook `a` has been created."
    assert len(notebook_controller.db.data) == 1
    config: NotebookConfig = notebook_controller.db.select_all()[0]
    assert config.stage == Stage.NOT_STARTED
    assert config.desired_stage == Stage.RUNNING

    run.assert_not_called()
    notebook_controller.run("a", "token")
    run.assert_called()
    notebook_obj_1 = notebook_controller.r["a"]
    assert isinstance(notebook_obj_1, notebook.JupyterLab)
    assert notebook_obj_1.collect_model() != config
    assert notebook_obj_1.collect_model().stage == Stage.PENDING

    notebook_obj_1._url = "abc"
    notebook_controller.run("a", "token")
    assert notebook_obj_1.stage == Stage.PENDING

    stop.assert_not_called()
    response = notebook_controller.stop_notebook(config)
    assert response == "The notebook `a` has been stopped."

    response = notebook_controller.stop_notebook(config)
    assert response == "The notebook `a` is already stopped."

    notebook_controller.run("a", "token")
    stop.assert_called()
    assert notebook_obj_1.collect_model().stage == Stage.STOPPING
    notebook_obj_1._calls = {
        CacheCallsKeys.LATEST_CALL_HASH: "call_1",
        "call_1": {"statuses": [{"stage": Stage.STOPPED, "timestamp": 1, "reason": None}]},
    }
    notebook_controller.run("a", "token")
    config = notebook_controller.db.select_all()[0]
    assert config.stage == Stage.STOPPED

    response = notebook_controller.run_notebook(config)
    config = notebook_controller.db.select_all()[0]
    assert config.stage == Stage.STOPPED
    assert config.desired_stage == Stage.RUNNING
    assert response == "The notebook `a` has been updated."
    notebook_controller.run("a", "token")
    assert isinstance(notebook_controller.r["a"], notebook.JupyterLab)
    assert notebook_controller.r["a"] != notebook_obj_1

    del notebook_controller.r["a"]
    response = notebook_controller.stop_notebook(config)
    assert response == "You don't have any notebooks. Create a notebook with `lightning run notebook --name=my_name`."
