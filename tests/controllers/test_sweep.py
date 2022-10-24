import os

from lightning_hpo.commands.data.create import DataConfig
from lightning_hpo.commands.sweep.run import SweepConfig
from lightning_hpo.commands.tensorboard.stop import TensorboardConfig
from lightning_hpo.components.sweep import Sweep
from lightning_hpo.controllers import controller
from lightning_hpo.controllers.sweep import SweepController
from lightning_hpo.distributions.distributions import Uniform
from lightning_hpo.utilities.enum import Stage
from tests.helpers import MockDatabaseClient, MockObjective


def test_sweep_controller(monkeypatch):

    sweep = Sweep(
        sweep_id="a",
        script_path=__file__,
        total_experiments=5,
        requirements=[],
        parallel_experiments=1,
        logger="tensorboard",
        distributions={"best_model_score": Uniform(1, 10)},
        framework="pytorch_lightning",
        data={"a/": None},
    )
    sweep_controller = SweepController()
    sweep_controller.db_url = "a"
    monkeypatch.setattr(controller, "DatabaseClient", MockDatabaseClient)
    config: SweepConfig = sweep.collect_model()
    assert "best_model_score" in config.distributions
    response = sweep_controller.run_sweep(config)
    assert response == "The provided Data 'a/' doesn't exist."
    sweep_controller.db._session.model = [SweepConfig, DataConfig, TensorboardConfig]
    mount_config = DataConfig(name="a/", source="s3://a/", mount_path=os.path.dirname(__file__) + "/")
    sweep_controller.db.insert(mount_config)
    response = sweep_controller.run_sweep(config)
    assert response == "Launched a Sweep 'a'."
    assert sweep_controller.db.data["SweepConfig:a"] == config
    assert len(sweep_controller.db.select_all(SweepConfig)) == 1

    assert sweep_controller.tensorboard_sweep_id is None
    sweep_controller.run("a", "b")
    assert isinstance(sweep_controller.r["a"], Sweep)
    sweep_controller.r["a"] = sweep
    sweep_controller.r["a"]._objective_cls = MockObjective
    assert len(sweep_controller.db.select_all(TensorboardConfig)) == 1
    assert sweep_controller.tensorboard_sweep_id == ["a"]
    response = sweep_controller.run_sweep(config)
    assert response == "The current Sweep 'a' is running. It couldn't be updated."

    while True:
        sweep_controller.run("a", "b")
        if sweep_controller.r.get("a", None) is None:
            break

    assert sweep_controller.db.data["SweepConfig:a"]["stage"] == Stage.SUCCEEDED
