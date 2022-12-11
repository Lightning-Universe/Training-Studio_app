import json
import os
from copy import deepcopy
from unittest.mock import MagicMock

import requests
from lightning.app.storage import Drive

from lightning_training_studio.commands.experiment.stop import StopExperimentConfig
from lightning_training_studio.components.sweep import Sweep, SweepConfig
from lightning_training_studio.controllers.sweep import SweepController
from lightning_training_studio.utilities.enum import Stage


def test_stop_sweeps_experiment(monkeypatch):

    with open(os.path.join(os.path.dirname(__file__), "../sweep/sweep_1.json"), "rb") as f:
        data = json.load(f)

    sweep_config = SweepConfig(**data[0])
    experiment = deepcopy(sweep_config.experiments[0])
    experiment.stage = Stage.RUNNING
    sweep_config.experiments[1] = experiment
    sweep_config.logger = "streamlit"
    sweep = Sweep.from_config(config=sweep_config)

    sweep_controller = SweepController(Drive("lit://code"))
    sweep_controller._db_client = MagicMock()
    sweep_controller.r[sweep_config.sweep_id] = sweep
    resp = MagicMock()
    resp.status_code = 200
    monkeypatch.setattr(requests, "put", MagicMock(return_value=resp))

    sweep_mock = MagicMock()
    sweep_mock.collect_model.return_value = sweep_config
    sweep_controller.r[sweep_config.sweep_id] = sweep_mock
    sweep_controller._db_client.select_all.return_value = [sweep_config]
    result = sweep_controller.stop_experiment(config=StopExperimentConfig(name="a"))
    assert result == "The current experiment `a` has been stopped."
    sweep_controller.r[sweep_config.sweep_id].stop_experiment.assert_called()
    result = sweep_controller.stop_experiment(config=StopExperimentConfig(name="aa"))
    assert result == "The current experiment `aa` doesn't exist."
