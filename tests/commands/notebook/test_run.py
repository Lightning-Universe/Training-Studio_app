from unittest.mock import MagicMock

import lightning_hpo.controllers.notebook as controller_notebook
from lightning_hpo.commands.notebook.run import NotebookConfig
from lightning_hpo.commands.notebook.stop import StopNotebookConfig
from lightning_hpo.controllers import controller
from lightning_hpo.controllers.notebook import NotebookController
from lightning_hpo.utilities.enum import State
from tests.helpers import MockDatabaseConnector


def test_notebook(monkeypatch):

    notebook_controller = NotebookController()
    monkeypatch.setattr(controller, "DatabaseConnector", MockDatabaseConnector)
    notebook = MagicMock()
    jupyterlab = MagicMock(return_value=notebook)
    monkeypatch.setattr(controller_notebook, "JupyterLab", jupyterlab)
    notebook_controller.run("a")
    assert notebook_controller.db.data == {}

    notebook_config = NotebookConfig(name="a", cloud_compute="cpu", requirements=[])
    response = notebook_controller.run_notebook(notebook_config)
    assert response == "The notebook `a` has been created."
    assert len(notebook_controller.db.data) == 1
    config = NotebookConfig(**list(notebook_controller.db.data.values())[0])

    assert config.notebook_name == "a"
    assert config.state == State.NOT_STARTED
    assert config.desired_state == State.RUNNING

    config.state = State.RUNNING
    notebook.updates = [config]
    notebook_controller.run("a")
    assert isinstance(notebook_controller.r["a"], MagicMock)
    notebook_controller.r["a"].run.assert_called()
    config = NotebookConfig(**list(notebook_controller.db.data.values())[0])
    assert config.state == State.RUNNING

    response = notebook_controller.show_notebook()
    assert len(response) == 1
    assert response[0] == config

    notebook_controller.r["a"].config = config.dict()
    response = notebook_controller.stop_notebook(StopNotebookConfig(name=config.notebook_name))
    assert "The notebook `a` has been stopped."
    config = NotebookConfig(**list(notebook_controller.db.data.values())[0])
    assert config.state == State.STOPPED
    assert config.desired_state == State.STOPPED

    response = notebook_controller.stop_notebook(StopNotebookConfig(name=config.notebook_name))
    assert "The notebook `a` is already stopped."

    del notebook_controller.r["a"]
    response = notebook_controller.stop_notebook(StopNotebookConfig(name=config.notebook_name))
    assert "The notebook `a` doesn't exist."
