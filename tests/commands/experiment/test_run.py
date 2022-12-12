import os
import sys
from unittest.mock import MagicMock

import pytest

from lightning_training_studio.commands.experiment import run
from lightning_training_studio.commands.sweep.run import SweepConfig
from tests.helpers import _create_client_command_mock


def test_experiment_run_parsing_file_absent(monkeypatch):

    monkeypatch.setattr(sys, "argv", ["", "a"])

    with pytest.raises(FileNotFoundError, match="The provided script doesn't exist"):
        command = _create_client_command_mock(run.RunExperimentCommand, None, MagicMock(), MagicMock())
        command.run()


def test_experiment_run_parsing_no_arguments(monkeypatch):

    monkeypatch.setattr(run, "CustomLocalSourceCodeDir", MagicMock())

    monkeypatch.setattr(sys, "argv", ["", __file__])

    def check(config: SweepConfig):
        exp = run.ExperimentConfig(
            name="",
            best_model_score=None,
            monitor=None,
            best_model_path=None,
            stage="not_started",
            params={},
            exception=None,
            progress=None,
            total_parameters=None,
            start_time=None,
            end_time=None,
        )
        exp.name = config.experiments[0].name
        expected = SweepConfig(
            sweep_id="",
            script_path=__file__,
            total_experiments=1,
            parallel_experiments=1,
            total_experiments_done=0,
            requirements=[],
            packages=[],
            script_args=[],
            algorithm="",
            distributions={},
            logger_url="",
            experiments={0: exp},
            framework="pytorch_lightning",
            cloud_compute="cpu",
            num_nodes=1,
            logger="tensorboard",
            direction="minimize",
            stage="not_started",
            desired_stage="running",
            disk_size=80,
            pip_install_source=False,
            data={},
        )
        expected.sweep_id = config.sweep_id
        expected.username = config.username
        assert config == expected

    command = _create_client_command_mock(run.RunExperimentCommand, None, MagicMock(), check)
    command.run()


def test_experiment_run_parsing_arguments(monkeypatch):

    monkeypatch.setattr(run, "CustomLocalSourceCodeDir", MagicMock())

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "",
            __file__,
            "--data",
            "example",
            "--requirements",
            "'jsonargparse[signatures]'",
            "--model.lr=0.1",
            "--cloud_compute",
            "cpu-medium",
        ],
    )

    def check(config: SweepConfig):
        exp = run.ExperimentConfig(
            name="",
            best_model_score=None,
            monitor=None,
            best_model_path=None,
            stage="not_started",
            params={},
            exception=None,
            progress=None,
            total_parameters=None,
            start_time=None,
            end_time=None,
        )
        exp.name = config.experiments[0].name
        expected = SweepConfig(
            sweep_id="",
            script_path=__file__,
            total_experiments=1,
            parallel_experiments=1,
            total_experiments_done=0,
            requirements=["'jsonargparse[signatures]'"],
            packages=[],
            script_args=["--model.lr=0.1"],
            algorithm="",
            distributions={},
            logger_url="",
            experiments={0: exp},
            framework="pytorch_lightning",
            cloud_compute="cpu-medium",
            num_nodes=1,
            logger="tensorboard",
            direction="minimize",
            stage="not_started",
            desired_stage="running",
            disk_size=80,
            pip_install_source=False,
            data={"example": None},
        )
        expected.sweep_id = config.sweep_id
        expected.username = config.username
        assert config == expected

    command = _create_client_command_mock(run.RunExperimentCommand, None, MagicMock(), check)
    command.run()


def test_experiment_run_multiple_requirements(monkeypatch):

    monkeypatch.setattr(run, "CustomLocalSourceCodeDir", MagicMock())

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "",
            __file__,
            "--requirements",
            "'jsonargparse[signatures]'",
            "deepspeed",
        ],
    )

    def check(config: SweepConfig):
        assert config.requirements == ["'jsonargparse[signatures]'", "deepspeed"]

    command = _create_client_command_mock(run.RunExperimentCommand, None, MagicMock(), check)
    command.run()


def test_experiment_run_multiple_packages(monkeypatch):

    monkeypatch.setattr(run, "CustomLocalSourceCodeDir", MagicMock())

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "",
            __file__,
            "--packages",
            "redis",
            "ffmpeg",
        ],
    )

    def check(config: SweepConfig):
        assert config.packages == ["redis", "ffmpeg"]

    command = _create_client_command_mock(run.RunExperimentCommand, None, MagicMock(), check)
    command.run()


def test_experiment_run_parsing_requirements(monkeypatch):

    monkeypatch.setattr(run, "CustomLocalSourceCodeDir", MagicMock())

    requirements_file = os.path.join(os.path.dirname(__file__), "test_requirements")
    monkeypatch.setattr(sys, "argv", ["", __file__, "--requirements", requirements_file])

    def check(config: SweepConfig):
        exp = run.ExperimentConfig(
            name="",
            best_model_score=None,
            monitor=None,
            best_model_path=None,
            stage="not_started",
            params={},
            exception=None,
            progress=None,
            total_parameters=None,
            start_time=None,
            end_time=None,
        )
        exp.name = config.experiments[0].name
        expected = SweepConfig(
            sweep_id="",
            script_path=__file__,
            total_experiments=1,
            parallel_experiments=1,
            total_experiments_done=0,
            requirements=["pytorch_lightning", "optuna", "deepspeed"],
            packages=[],
            script_args=[],
            algorithm="",
            distributions={},
            logger_url="",
            experiments={0: exp},
            framework="pytorch_lightning",
            cloud_compute="cpu",
            num_nodes=1,
            logger="tensorboard",
            direction="minimize",
            stage="not_started",
            desired_stage="running",
            disk_size=80,
            pip_install_source=False,
            data={},
        )
        expected.sweep_id = config.sweep_id
        expected.username = config.username
        assert config == expected

    command = _create_client_command_mock(run.RunExperimentCommand, None, MagicMock(), check)
    command.run()


def test_experiment_run_parsing_pip_install(monkeypatch):

    monkeypatch.setattr(run, "CustomLocalSourceCodeDir", MagicMock())

    monkeypatch.setattr(sys, "argv", ["", __file__, "--pip-install-source"])

    def check(config: SweepConfig):
        exp = run.ExperimentConfig(
            name="",
            best_model_score=None,
            monitor=None,
            best_model_path=None,
            stage="not_started",
            params={},
            exception=None,
            progress=None,
            total_parameters=None,
            start_time=None,
            end_time=None,
        )
        exp.name = config.experiments[0].name
        expected = SweepConfig(
            sweep_id="",
            script_path=__file__,
            total_experiments=1,
            parallel_experiments=1,
            total_experiments_done=0,
            requirements=[],
            packages=[],
            script_args=[],
            algorithm="",
            distributions={},
            logger_url="",
            experiments={0: exp},
            framework="pytorch_lightning",
            cloud_compute="cpu",
            num_nodes=1,
            logger="tensorboard",
            direction="minimize",
            stage="not_started",
            desired_stage="running",
            disk_size=80,
            pip_install_source=True,
            data={},
        )
        expected.sweep_id = config.sweep_id
        expected.username = config.username
        assert config == expected

    command = _create_client_command_mock(run.RunExperimentCommand, None, MagicMock(), check)
    command.run()
