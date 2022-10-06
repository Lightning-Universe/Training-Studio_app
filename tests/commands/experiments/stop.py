import json
import os
from copy import deepcopy
from unittest.mock import MagicMock

import requests
from lightning.app.storage import Drive

from lightning_hpo.commands.experiment.stop import StopExperimentConfig
from lightning_hpo.components.sweep import Sweep, SweepConfig
from lightning_hpo.controllers.sweep import SweepController
from lightning_hpo.utilities.enum import Stage


def test_stop_sweeps_experiment(monkeypatch):

    with open(os.path.join(os.path.dirname(__file__), "../sweep/sweep_1.json"), "rb") as f:
        data = json.load(f)

    sweep_config = SweepConfig(**data[0])
    trial = deepcopy(sweep_config.trials[0])
    trial.stage = Stage.RUNNING
    sweep_config.trials[1] = trial
    sweep_config.logger = "streamlit"
    sweep = Sweep.from_config(config=sweep_config)

    sweep_controller = SweepController(Drive("lit://code"))
    sweep_controller._database = MagicMock()
    sweep_controller.r[sweep_config.sweep_id] = sweep
    resp = MagicMock()
    resp.status_code = 200
    monkeypatch.setattr(requests, "put", MagicMock(return_value=resp))

    sweep_mock = MagicMock()
    sweep_mock.collect_model.return_value = sweep_config
    sweep_controller.r[sweep_config.sweep_id] = sweep_mock
    sweep_controller._database.get.return_value = [sweep_config]
    result = sweep_controller.stop_experiment(config=StopExperimentConfig(name="a"))
    assert result == "The current trial `a` has been stopped."
    sweep_controller.r[sweep_config.sweep_id].stop_experiment.assert_called()
    result = sweep_controller.stop_experiment(config=StopExperimentConfig(name="aa"))
    assert result == "The current trial `aa` doesn't exist."
