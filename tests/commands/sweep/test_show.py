import json
import os
import sys
from unittest.mock import MagicMock

import pytest
import requests
from lightning.app.storage import Drive
from rich.table import Table

from lightning_hpo.commands.sweep import show
from lightning_hpo.commands.sweep.show import ShowSweepsCommand
from lightning_hpo.components.sweep import Sweep, SweepConfig
from lightning_hpo.controllers.sweeper import SweepController


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
        sys.argv = ["", "--sweep_id=1234"]
        command = ShowSweepsCommand(None)
        command.command_name = ""
        command.app_url = ""
        command.run()

    monkeypatch.setattr(show, "Console", console)
    sys.argv = ["", "--sweep_id=thomas-cb8f69f0"]
    command = ShowSweepsCommand(None)
    command.command_name = ""
    command.app_url = ""
    command.run()
    assert len(console._mock_mock_calls) == 6
    table = console._mock_mock_calls[-1].args[0]
    assert isinstance(table, Table)
    assert table.columns[3]._cells[0] == "{'model.lr': 0.04490742315966646}"

    sys.argv = ori_sys_argv


def test_show_sweeps_server(monkeypatch):

    with open(os.path.join(os.path.dirname(__file__), "sweep_1.json"), "rb") as f:
        data = json.load(f)

    sweep_config = SweepConfig(**data[0])
    sweep_config.logger = "streamlit"
    Sweep.from_config(config=sweep_config)

    sweep_controller = SweepController(Drive("lit://code"))
    sweep_controller.db_url = ""
    resp = MagicMock()
    resp.json.return_value = data
    resp.status_code = 200
    get = MagicMock(return_value=resp)
    monkeypatch.setattr(requests, "get", get)
    result = sweep_controller.show_sweeps()
    assert result == data
    expected = '{"cls_name": "SweepConfig", "cls_module": "lightning_hpo.commands.sweep.run", "data": "", "id": null}'
    assert get._mock_call_args.kwargs["data"] == expected
