import json
import os
import sys
from unittest.mock import MagicMock

import pytest
import requests
from rich.table import Table

from lightning_hpo.commands.sweep import show_sweeps
from lightning_hpo.commands.sweep.show_sweeps import ShowSweepsCommand


def test_show_sweeps_client(monkeypatch):

    ori_sys_argv = sys.argv

    with open(os.path.join(os.path.dirname(__file__), "sweep_1.json"), "rb") as f:
        data = json.load(f)

    resp = MagicMock()
    resp.json.return_value = data
    resp.status_code = 200
    monkeypatch.setattr(requests, "post", MagicMock(return_value=resp))
    console = MagicMock()

    monkeypatch.setattr(show_sweeps, "Console", console)
    sys.argv = [""]
    command = ShowSweepsCommand(None)
    command.command_name = ""
    command.app_url = ""
    command.run()
    assert len(console._mock_mock_calls) == 2
    table = console._mock_mock_calls[1].args[0]
    assert isinstance(table, Table)
    assert table.columns[0]._cells == ["thomas-cb8f69f0"]

    monkeypatch.setattr(show_sweeps, "Console", console)
    with pytest.raises(Exception, match="thomas-cb8f69f0"):
        sys.argv = ["", "--sweep_id=1234"]
        command = ShowSweepsCommand(None)
        command.command_name = ""
        command.app_url = ""
        command.run()

    monkeypatch.setattr(show_sweeps, "Console", console)
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
