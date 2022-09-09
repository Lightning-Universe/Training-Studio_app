import json
import os
from copy import deepcopy
from unittest.mock import MagicMock

import requests
from lightning.app.storage import Drive

from lightning_hpo.commands.sweep.stop import StopSweepConfig
from lightning_hpo.components.sweep import Sweep, SweepConfig
from lightning_hpo.controllers.sweep import SweepController
from lightning_hpo.utilities.enum import State


def test_stop_sweeps_server(monkeypatch):

    with open(os.path.join(os.path.dirname(__file__), "sweep_1.json"), "rb") as f:
        data = json.load(f)

    sweep_config = SweepConfig(**data[0])
    trial = deepcopy(sweep_config.trials[0])
    trial.stage = State.RUNNING
    sweep_config.trials[1] = trial
    sweep_config.logger = "streamlit"
    sweep = Sweep.from_config(config=sweep_config)

    sweep_controller = SweepController(Drive("lit://code"))
    sweep_controller._database = MagicMock()
    sweep_controller.r[sweep_config.sweep_id] = sweep
    resp = MagicMock()
    resp.status_code = 200
    monkeypatch.setattr(requests, "put", MagicMock(return_value=resp))
    result = sweep_controller.stop_sweep(config=StopSweepConfig(sweep_id=sweep_config.sweep_id))
    assert result == "Stopped the sweep `thomas-cb8f69f0`"
    assert sweep.config["stage"] == State.STOPPED
    assert sweep.config["trials"][0].stage == State.SUCCEEDED
    assert sweep.config["trials"][1].stage == State.STOPPED
