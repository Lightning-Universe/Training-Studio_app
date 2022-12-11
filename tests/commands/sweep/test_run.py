import sys
from unittest.mock import MagicMock

import pytest

from lightning_training_studio.commands.sweep import run
from lightning_training_studio.commands.sweep.run import Distributions, RunSweepCommand
from tests.helpers import _create_client_command_mock


def run_sweep_command(monkeypatch, argv, check):
    monkeypatch.setattr(sys, "argv", argv)
    command = _create_client_command_mock(RunSweepCommand, None, MagicMock(), check)
    command.run()


def test_sweep_run_parsing_file_absent(monkeypatch):

    monkeypatch.setattr(run, "CustomLocalSourceCodeDir", MagicMock())

    with pytest.raises(ValueError, match="The provided script doesn't exist: train2.py"):
        monkeypatch.setattr(sys, "argv", ["python", "train2.py"])
        command = _create_client_command_mock(RunSweepCommand, None, MagicMock(), None)
        command.run()


def test_sweep_run_parsing_file_no_arguments(monkeypatch):

    monkeypatch.setattr(run, "CustomLocalSourceCodeDir", MagicMock())

    def check_0(config):
        assert config.distributions == {}
        assert config.algorithm == "grid_search"

    run_sweep_command(monkeypatch, ["python", __file__], check_0)

    def check_1(config):
        assert config.distributions == {}
        assert config.algorithm == "random_search"

    run_sweep_command(monkeypatch, ["python", __file__, "--algorithm=random_search"], check_1)


def test_sweep_run_parsing_file_single_list(monkeypatch):

    monkeypatch.setattr(run, "CustomLocalSourceCodeDir", MagicMock())

    def check_0(config):
        assert config.distributions == {
            "--lr": Distributions(distribution="categorical", params={"choices": [0.0, 1.0, 2.0]})
        }
        assert config.algorithm == "grid_search"

    argv = ["python", __file__, "--lr", "[0, 1, 2]"]
    run_sweep_command(monkeypatch, argv, check_0)


def test_sweep_run_parsing_file_two_lists(monkeypatch):

    monkeypatch.setattr(run, "CustomLocalSourceCodeDir", MagicMock())

    def check_0(config):
        assert config.distributions == {
            "--lr": Distributions(distribution="categorical", params={"choices": [0.0, 1.0, 2.0]}),
            "--gamma": Distributions(distribution="categorical", params={"choices": [0.0, 1.0, 2.0]}),
        }
        assert config.algorithm == "grid_search"

    argv = ["python", __file__, "--lr", "[0, 1, 2]", "--gamma", "[0.0, 1.0, 2.0]"]
    run_sweep_command(monkeypatch, argv, check_0)


def test_sweep_run_parsing_file_two_lists_hydra(monkeypatch):

    monkeypatch.setattr(run, "CustomLocalSourceCodeDir", MagicMock())

    def check_0(config):
        assert config.distributions == {
            "lr": Distributions(distribution="categorical", params={"choices": [0.0, 1.0, 2.0]}),
            "gamma": Distributions(distribution="categorical", params={"choices": [0.0, 1.0, 2.0]}),
        }
        assert config.algorithm == "grid_search"

    argv = ["python", __file__, "--syntax", "hydra", "lr=0,1,2", "gamma=0.0,1.0,2.0"]
    run_sweep_command(monkeypatch, argv, check_0)


def test_sweep_run_parsing_file_list_and_script_arguments(monkeypatch):

    monkeypatch.setattr(run, "CustomLocalSourceCodeDir", MagicMock())

    def check_0(config):
        assert config.distributions == {
            "--lr": Distributions(distribution="categorical", params={"choices": [0.0, 1.0, 2.0]}),
        }
        assert config.script_args == ["--data.batch=something"]

    argv = ["python", __file__, "--lr", "[0, 1, 2]", "--data.batch", "something"]
    run_sweep_command(monkeypatch, argv, check_0)


def test_sweep_run_parsing_range(monkeypatch):

    monkeypatch.setattr(run, "CustomLocalSourceCodeDir", MagicMock())

    def check_0(config):
        assert config.distributions == {
            "--lr": Distributions(
                distribution="categorical", params={"choices": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]}
            ),
        }
        assert config.script_args == ["--data.batch=something"]

    argv = ["python", __file__, "--lr", "range(0, 10)", "--data.batch", "something"]
    run_sweep_command(monkeypatch, argv, check_0)


def test_sweep_run_parsing_range_hydra(monkeypatch):

    monkeypatch.setattr(run, "CustomLocalSourceCodeDir", MagicMock())

    def check_0(config):
        assert config.distributions == {
            "lr": Distributions(
                distribution="categorical", params={"choices": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]}
            ),
        }
        assert config.script_args == ["data.batch=something"]

    argv = ["python", __file__, "--syntax", "hydra", "lr=range(0, 10)", "data.batch=something"]
    run_sweep_command(monkeypatch, argv, check_0)


def test_sweep_run_parsing_random_search(monkeypatch):

    monkeypatch.setattr(run, "CustomLocalSourceCodeDir", MagicMock())

    def check_0(config):
        assert config.distributions == {
            "--lr": Distributions(
                distribution="categorical", params={"choices": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]}
            ),
        }
        assert config.script_args == ["--data.batch=something"]

    argv = [
        "python",
        __file__,
        "--lr",
        "range(0, 10)",
        "--data.batch",
        "something",
        "--algorithm",
        "random_search",
        "--total_experiments",
        "10",
    ]
    run_sweep_command(monkeypatch, argv, check_0)

    def check_1(config):
        assert config.distributions == {
            "--lr": Distributions(distribution="categorical", params={"choices": [0.0, 1.0, 2.0]}),
        }

    argv = [
        "python",
        __file__,
        "--lr",
        "[0, 1, 2]",
        "--data.batch",
        "something",
        "--algorithm",
        "random_search",
        "--total_experiments",
        "3",
    ]
    run_sweep_command(monkeypatch, argv, check_1)

    def check_2(config):
        assert {
            "--lr": Distributions(distribution="categorical", params={"choices": [0.0, 2.0]}),
            "--batch_size": Distributions(
                distribution="categorical", params={"choices": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]}
            ),
        }
        assert config.script_args == ["--data.batch=something"]

    argv = [
        "python",
        __file__,
        "--lr",
        "[0, 2]",
        "--batch_size",
        "range(0, 10)",
        "--data.batch",
        "something",
        "--algorithm",
        "random_search",
        "--total_experiments",
        "10",
    ]
    run_sweep_command(monkeypatch, argv, check_2)


def test_sweep_run_parsing_random_search_hydra(monkeypatch):

    monkeypatch.setattr(run, "CustomLocalSourceCodeDir", MagicMock())

    def check_0(config):
        assert config.distributions == {
            "lr": Distributions(
                distribution="categorical", params={"choices": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]}
            ),
        }
        assert config.script_args == ["data.batch=something"]

    argv = [
        "python",
        __file__,
        "--syntax",
        "hydra",
        "--algorithm",
        "random_search",
        "--total_experiments",
        "10",
        "lr=range(0, 10)",
        "data.batch=something",
    ]
    run_sweep_command(monkeypatch, argv, check_0)

    def check_1(config):
        assert config.distributions == {
            "lr": Distributions(distribution="categorical", params={"choices": [0.0, 1.0, 2.0]}),
        }

    argv = [
        "python",
        __file__,
        "--syntax",
        "hydra",
        "--algorithm",
        "random_search",
        "--total_experiments",
        "3",
        "lr=0,1,2",
        "data.batch=something",
    ]
    run_sweep_command(monkeypatch, argv, check_1)

    def check_2(config):
        assert {
            "lr": Distributions(distribution="categorical", params={"choices": [0.0, 2.0]}),
            "batch_size": Distributions(
                distribution="categorical", params={"choices": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]}
            ),
        }
        assert config.script_args == ["data.batch=something"]

    argv = [
        "python",
        __file__,
        "--syntax",
        "hydra",
        "--algorithm",
        "random_search",
        "--total_experiments",
        "10",
        "lr=0,2",
        "batch_size=range(0, 10)",
        "data.batch=something",
    ]
    run_sweep_command(monkeypatch, argv, check_2)


def test_sweep_run_parsing_random_search_further_distributions(monkeypatch):

    monkeypatch.setattr(run, "CustomLocalSourceCodeDir", MagicMock())

    def check_1(config):
        assert config.distributions == {
            "--lr": Distributions(distribution="categorical", params={"choices": [0.0, 2.0]}),
            "--batch_size": Distributions(
                distribution="categorical", params={"choices": [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]}
            ),
            "--gamma": Distributions(distribution="log_uniform", params={"low": 32.0, "high": 64.0}),
        }
        assert config.script_args == ["--data.batch=something"]

    argv = [
        "python",
        __file__,
        "--lr",
        "[0, 2]",
        "--batch_size",
        "range(0, 10)",
        "--gamma",
        "log_uniform(32, 64)",
        "--data.batch",
        "something",
        "--algorithm",
        "random_search",
        "--total_experiments",
        "10",
    ]
    run_sweep_command(monkeypatch, argv, check_1)


def test_parsing(monkeypatch):

    monkeypatch.setattr(run, "CustomLocalSourceCodeDir", MagicMock())

    def check(config):
        assert config.distributions == {
            "--model.lr": Distributions(distribution="categorical", params={"choices": [0.001]}),
            "--data.batch": Distributions(distribution="categorical", params={"choices": [32.0, 64.0]}),
        }
        assert config.script_args == ["--something=else"]

    argv = f"python {__file__} --model.lr [0.001] --data.batch [32, 64] --something=else".split(" ")
    run_sweep_command(monkeypatch, argv, check)
