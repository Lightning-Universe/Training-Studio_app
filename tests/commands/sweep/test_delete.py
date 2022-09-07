import json
import os
from copy import deepcopy
from unittest.mock import MagicMock

from lightning.app.storage import Drive
from sqlmodel import create_engine, SQLModel

from lightning_hpo.commands.sweep.delete import DeleteSweepConfig
from lightning_hpo.components.servers.db import server
from lightning_hpo.components.servers.db.server import general_delete, general_get, general_post, GeneralModel
from lightning_hpo.components.sweep import Sweep, SweepConfig
from lightning_hpo.controllers.sweep import SweepController
from lightning_hpo.utilities.enum import Status


def test_delete_sweeps_server(monkeypatch, tmpdir):

    with open(os.path.join(os.path.dirname(__file__), "sweep_1.json"), "rb") as f:
        data = json.load(f)

    sweep_config = SweepConfig(**data[0])
    trial = deepcopy(sweep_config.trials[0])
    trial.status = Status.RUNNING
    sweep_config.trials[1] = trial
    sweep_config.logger = "streamlit"
    sweep = Sweep.from_config(config=sweep_config)

    sweep_controller = SweepController(Drive("lit://code"))
    db = MagicMock()
    sweep_controller._database = db
    sweep_controller.r[sweep_config.sweep_id] = sweep
    result = sweep_controller.delete_sweep(config=DeleteSweepConfig(sweep_id=sweep_config.sweep_id))
    assert result == "Deleted the sweep `thomas-cb8f69f0`"
    assert sweep_controller.r == {}

    general = GeneralModel.from_obj(db.delete._mock_call_args[0][0], id="sweep_id")
    engine = create_engine(f"sqlite:///{tmpdir}/database.db", echo=True)
    SQLModel.metadata.create_all(engine)
    monkeypatch.setattr(server, "engine", engine)
    general_post(GeneralModel.from_obj(sweep_config, id="sweep_id"))
    assert len(general_get(GeneralModel.from_cls(SweepConfig))) == 1
    general_delete(general)
    assert general_get(GeneralModel.from_cls(SweepConfig)) == []
