from unittest.mock import MagicMock

from lightning_hpo.commands.notebook.run import NotebookConfig
from lightning_hpo.controllers import controller, notebook
from lightning_hpo.controllers.notebook import NotebookController
from lightning_hpo.utilities.enum import Stage
from tests.helpers import MockDatabaseConnector


def test_notebook_controller(monkeypatch):

    notebook_controller = NotebookController()
    monkeypatch.setattr(controller, "DatabaseConnector", MockDatabaseConnector)
    run = MagicMock()
    stop = MagicMock()
    monkeypatch.setattr(notebook.JupyterLab, "run", run)
    monkeypatch.setattr(notebook.JupyterLab, "stop", stop)
    notebook_controller.run("a")
    assert notebook_controller.db.data == {}

    config = NotebookConfig(notebook_name="a", requirements=[], cloud_compute="cpu")
    response = notebook_controller.run_notebook(config)
    assert response == "The notebook `a` has been created."
    assert len(notebook_controller.db.data) == 1
    config: NotebookConfig = notebook_controller.db.get()[0]
    assert config.stage == Stage.NOT_STARTED
    assert config.desired_stage == Stage.RUNNING

    run.assert_not_called()
    notebook_controller.run("a")
    run.assert_called()
    notebook_obj_1 = notebook_controller.r["a"]
    assert isinstance(notebook_obj_1, notebook.JupyterLab)
    assert notebook_obj_1.collect_model() != config
    assert notebook_obj_1.collect_model().stage == Stage.PENDING

    notebook_obj_1._url = "abc"
    notebook_controller.run("a")
    assert notebook_obj_1.stage == Stage.PENDING

    stop.assert_not_called()
    response = notebook_controller.stop_notebook(config)
    stop.assert_called()
    assert response == "The notebook `{config.name}` has been stopped."
    assert notebook_controller.r == {}
    config = notebook_controller.db.get()[0]
    assert config.stage == Stage.STOPPED
    assert config.desired_stage == Stage.STOPPED

    response = notebook_controller.run_notebook(config)
    config = notebook_controller.db.get()[0]
    assert config.stage == Stage.STOPPED
    assert config.desired_stage == Stage.RUNNING
    assert response == "The notebook `a` has been updated."
    notebook_controller.run("a")
    assert isinstance(notebook_controller.r["a"], notebook.JupyterLab)
    assert notebook_controller.r["a"] != notebook_obj_1
