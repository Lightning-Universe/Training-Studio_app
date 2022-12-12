import json
import os
import sys
from unittest.mock import MagicMock

import pytest
import requests
from lightning.app.storage import Drive
from rich.table import Table

from lightning_training_studio.commands.sweep import show
from lightning_training_studio.commands.sweep.show import ShowSweepsCommand
from lightning_training_studio.components.sweep import Sweep, SweepConfig
from lightning_training_studio.controllers.sweep import SweepController


def test_show_sweeps_client(monkeypatch):

    ori_sys_argv = sys.argv

    with open(os.path.join(os.path.dirname(__file__), "sweep_1.json"), "rb") as f:
        data = json.load(f)

    resp = MagicMock()
    resp.json.return_value = data
    resp.status_code = 200
    monkeypatch.setattr(requests, "post", MagicMock(return_value=resp))
    console = MagicMock()

    monkeypatch.setattr(show, "Console", console)
    sys.argv = [""]
    command = ShowSweepsCommand(None)
    command.command_name = ""
    command.app_url = ""
    command.run()
    assert len(console._mock_mock_calls) == 2
    table = console._mock_mock_calls[1].args[0]
    assert isinstance(table, Table)
    assert table.columns[0]._cells == ["thomas-cb8f69f0"]

    monkeypatch.setattr(show, "Console", console)
    with pytest.raises(Exception, match="thomas-cb8f69f0"):
        sys.argv = ["", "--name=1234"]
        command = ShowSweepsCommand(None)
        command.command_name = ""
        command.app_url = ""
        command.run()

    monkeypatch.setattr(show, "Console", console)
    sys.argv = ["", "--name=thomas-cb8f69f0"]
    command = ShowSweepsCommand(None)
    command.command_name = ""
    command.app_url = ""
    command.run()
    assert len(console._mock_mock_calls) == 4
    table = console._mock_mock_calls[-1].args[0]
    assert isinstance(table, Table)
    assert table.columns[3]._cells[0] == "3"

    sys.argv = ori_sys_argv


def test_show_sweeps_server():
    with open(os.path.join(os.path.dirname(__file__), "sweep_1.json"), "rb") as f:
        data = json.load(f)

    sweep_config = SweepConfig(**data[0])
    sweep_config.logger = "streamlit"
    Sweep.from_config(config=sweep_config)

    sweep_controller = SweepController(Drive("lit://code"))
    sweep_controller._db_client = MagicMock()
    sweep_controller.db_url = "a"
    sweep_controller._db_client.select_all.return_value = [sweep_config]
    result = sweep_controller.show_sweeps()
    assert result[0] == sweep_config.dict()
