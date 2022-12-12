import os
from unittest.mock import MagicMock

from lightning_training_studio.commands.data.create import DataConfig
from lightning_training_studio.commands.experiment.delete import DeleteExperimentConfig
from lightning_training_studio.commands.experiment.run import ExperimentConfig
from lightning_training_studio.commands.sweep.delete import DeleteSweepConfig
from lightning_training_studio.commands.sweep.run import SweepConfig
from lightning_training_studio.commands.tensorboard.stop import TensorboardConfig
from lightning_training_studio.components.sweep import Sweep
from lightning_training_studio.components.tensorboard import Tensorboard
from lightning_training_studio.controllers import controller
from lightning_training_studio.controllers.sweep import SweepController
from lightning_training_studio.controllers.tensorboard import TensorboardController
from lightning_training_studio.distributions.distributions import Uniform
from lightning_training_studio.utilities.enum import Stage
from tests.helpers import MockDatabaseClient, MockObjective


def test_sweep_controller(monkeypatch):

    sweep = Sweep(
        sweep_id="a",
        script_path=__file__,
        total_experiments=5,
        requirements=[],
        packages=[],
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
        sweep: Sweep = sweep_controller.r.get("a", None)
        sweep.data = None
        sweep_controller.run("a", "b")
        if sweep.stage == Stage.SUCCEEDED:
            break

    assert sweep_controller.db.data["SweepConfig:a"]["stage"] == Stage.SUCCEEDED


def _sweep_controller_setup(monkeypatch, sweep):
    monkeypatch.setattr(controller, "DatabaseClient", MockDatabaseClient)

    monkeypatch.setattr(Tensorboard, "stop", MagicMock())

    sweep_controller = SweepController()
    sweep_controller.db_url = "a"

    tensorboard_controller = TensorboardController()
    tensorboard_controller.db_url = "a"

    config: SweepConfig = sweep.collect_model()

    tensorboard_controller.db.data = sweep_controller.db.data
    tensorboard_controller.db._session = sweep_controller.db._session

    response = sweep_controller.run_sweep(config)
    sweep_controller.db._session.model = [SweepConfig, DataConfig, TensorboardConfig]

    assert response == "Launched a Sweep 'a'."

    assert sweep_controller.tensorboard_sweep_id is None
    sweep_controller.run("a", "b")
    assert isinstance(sweep_controller.r["a"], Sweep)
    sweep_controller.r["a"] = sweep
    sweep_controller.r["a"]._objective_cls = MockObjective

    tensorboard_configs = tensorboard_controller.db.select_all(TensorboardConfig)
    assert len(tensorboard_configs) == 1
    tensorboard_controller.on_reconcile_start(tensorboard_configs)

    return sweep_controller, tensorboard_controller, config


def test_sweep_controller_delete_sweep(monkeypatch):
    sweep = Sweep(
        sweep_id="a",
        script_path=__file__,
        total_experiments=2,
        requirements=[],
        parallel_experiments=2,
        logger="tensorboard",
        distributions={"best_model_score": Uniform(1, 10)},
        framework="pytorch_lightning",
        data={},
    )
    sweep_controller, tensorboard_controller, config = _sweep_controller_setup(monkeypatch, sweep)

    tensorboard_configs = tensorboard_controller.db.select_all(TensorboardConfig)
    assert len(tensorboard_configs) == 1
    delete_config = DeleteSweepConfig(name=config.sweep_id)
    sweep_controller.delete_sweep(delete_config)

    tensorboard_configs = tensorboard_controller.db.select_all(TensorboardConfig)
    tensorboard_controller.on_reconcile_start(tensorboard_configs)
    tensorboard_configs = tensorboard_controller.db.select_all(TensorboardConfig)
    assert len(tensorboard_controller.db.select_all(TensorboardConfig)) == 0


def test_sweep_controller_delete_xexperiment(monkeypatch):
    sweep = Sweep(
        sweep_id="a",
        script_path=__file__,
        total_experiments=1,
        requirements=[],
        parallel_experiments=1,
        logger="tensorboard",
        distributions={},
        experiments={0: ExperimentConfig(name="a", params={}).dict()},
        framework="pytorch_lightning",
        data={},
    )
    sweep_controller, tensorboard_controller, config = _sweep_controller_setup(monkeypatch, sweep)

    delete_config = DeleteSweepConfig(name=config.sweep_id)
    sweep_controller.delete_experiment(delete_config)

    tensorboard_configs = tensorboard_controller.db.select_all(TensorboardConfig)
    tensorboard_controller.on_reconcile_start(tensorboard_configs)

    assert len(sweep_controller.db.select_all(TensorboardConfig)) == 0


def test_sweep_controller_delete_experiment_from_sweep(monkeypatch):
    sweep = Sweep(
        sweep_id="a",
        script_path=__file__,
        total_experiments=2,
        requirements=[],
        parallel_experiments=2,
        logger="tensorboard",
        distributions={"best_model_score": Uniform(1, 10)},
        framework="pytorch_lightning",
        data={},
    )
    sweep_controller, tensorboard_controller, config = _sweep_controller_setup(monkeypatch, sweep)

    sweeps = sweep_controller.db.select_all(SweepConfig)
    assert len(sweeps) == 1
    assert len(sweeps[0].experiments) == 2

    delete_config = DeleteExperimentConfig(name=sweeps[0].experiments[0].name)

    sweep_controller.delete_experiment(delete_config)

    tensorboard_configs = tensorboard_controller.db.select_all(TensorboardConfig)
    tensorboard_controller.on_reconcile_start(tensorboard_configs)

    assert len(sweep_controller.db.select_all(TensorboardConfig)) == 1
