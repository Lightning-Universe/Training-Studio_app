import os
import re
from argparse import ArgumentParser
from getpass import getuser
from pathlib import Path
from typing import Dict, List, Optional, Union
from uuid import uuid4

import requests
from lightning.app.core.constants import APP_SERVER_HOST, APP_SERVER_PORT
from lightning.app.source_code import LocalSourceCodeDir
from lightning.app.source_code.uploader import FileUploader
from lightning.app.utilities.commands import ClientCommand
from sqlalchemy import Column
from sqlmodel import Field, SQLModel

from lightning_hpo.loggers import LoggerType
from lightning_hpo.utilities.enum import Stage
from lightning_hpo.utilities.utils import pydantic_column_type


class Distributions(SQLModel, table=False):
    distribution: str
    params: Dict[str, Union[float, int, str, List[float], List[str]]] = Field(
        sa_column=Column(pydantic_column_type(Dict[str, Union[float, int, List[float], List[str]]]))
    )


class TrialConfig(SQLModel, table=False):
    name: str
    best_model_score: Optional[float]
    monitor: Optional[str]
    best_model_path: Optional[str]
    stage: str = Stage.NOT_STARTED
    params: Dict[str, Union[float, int, str, List[float], List[str]]] = Field(
        sa_column=Column(pydantic_column_type(Dict[str, Union[float, int, List[float], List[str]]]))
    )
    exception: Optional[str]
    progress: Optional[float]
    total_parameters: Optional[str] = None
    start_time: Optional[str]
    end_time: Optional[str]

    @property
    def pruned(self) -> bool:
        return self.stage == Stage.PRUNED


class SweepConfig(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}

    sweep_id: str = Field(primary_key=True)
    script_path: str
    n_trials: int
    simultaneous_trials: int
    trials_done: int = 0
    requirements: List[str] = Field(..., sa_column=Column(pydantic_column_type(List[str])))
    script_args: List[str] = Field(..., sa_column=Column(pydantic_column_type(List[str])))
    algorithm: str
    distributions: Dict[str, Distributions] = Field(
        ..., sa_column=Column(pydantic_column_type(Dict[str, Distributions]))
    )
    logger_url: str = ""
    trials: Dict[int, TrialConfig] = Field(..., sa_column=Column(pydantic_column_type(Dict[int, TrialConfig])))
    framework: str
    cloud_compute: str = "cpu"
    num_nodes: int = 1
    logger: str
    direction: str
    stage: str = Stage.NOT_STARTED
    desired_stage: str = Stage.RUNNING
    disk_size: int = 80

    @property
    def num_trials(self) -> int:
        return min(self.trials_done + self.simultaneous_trials, self.n_trials)

    @property
    def username(self) -> str:
        return self.sweep_id.split("-")[0]

    @property
    def hash(self) -> str:
        return self.sweep_id.split("-")[1]

    def is_tensorboard(self):
        return self.logger == LoggerType.TENSORBOARD.value


class DistributionParser:
    @staticmethod
    def is_distribution(argument: str) -> bool:
        ...

    @staticmethod
    def parse(argument: str) -> Dict:
        ...


class UniformDistributionParser(DistributionParser):
    @staticmethod
    def is_distribution(argument: str) -> bool:
        return "uniform" in argument

    @staticmethod
    def parse(argument: str):
        name, value = argument.split("=")
        regex = "[0-9]*\.[0-9]*"  # noqa W605
        low, high = re.findall(regex, value)
        return {name: {"distribution": "uniform", "params": {"low": float(low), "high": float(high)}}}


class LogUniformDistributionParser(DistributionParser):
    @staticmethod
    def is_distribution(argument: str) -> bool:
        return "log_uniform" in argument

    @staticmethod
    def parse(argument: str):
        name, value = argument.split("=")
        regex = "[0-9]*\.[0-9]*"  # noqa W605
        low, high = re.findall(regex, value)
        return {name: {"distribution": "log_uniform", "params": {"low": float(low), "high": float(high)}}}


class CategoricalDistributionParser(DistributionParser):
    @staticmethod
    def is_distribution(argument: str) -> bool:
        return "categorical" in argument

    @staticmethod
    def parse(argument: str):
        name, value = argument.split("=")
        choices = value.split("[")[1].split("]")[0].split(", ")
        return {name: {"distribution": "categorical", "params": {"choices": choices}}}


class CustomFileUploader(FileUploader):
    def _upload_data(self, s: requests.Session, url: str, data: bytes):
        resp = s.put(url, files={"uploaded_file": data})
        assert resp.status_code == 200


class CustomLocalSourceCodeDir(LocalSourceCodeDir):
    def upload(self, url: str) -> None:
        """Uploads package to URL, usually pre-signed URL.

        Notes
        -----
        Since we do not use multipart uploads here, we cannot upload any
        packaged repository files which have a size > 2GB.

        This limitation should be removed during the datastore upload redesign
        """
        if self.package_path.stat().st_size > 2e9:
            raise OSError(
                "cannot upload directory code whose total fize size is greater than 2GB (2e9 bytes)"
            ) from None

        uploader = CustomFileUploader(
            presigned_url=url,
            source_file=str(self.package_path),
            name=self.package_path.name,
            total_size=self.package_path.stat().st_size,
        )
        uploader.upload()


def parse_distributions(script_args, args):
    distributions = {}
    for arg in args:
        is_distribution = False
        for p in [UniformDistributionParser, LogUniformDistributionParser, CategoricalDistributionParser]:
            if p.is_distribution(arg.replace("--", "")):
                distributions.update(p.parse(arg.replace("--", "")))
                is_distribution = True
                break
        if not is_distribution:
            script_args.append(arg)

    return {k: Distributions(distribution=x["distribution"], params=x["params"]) for k, x in distributions.items()}


def parse_args(args):
    parsed = {}

    # build a dict where key = arg, value = value of the arg or None if just a flag
    for i, arg_candidate in enumerate(args):
        arg = None
        value = None

        # only look at --keys
        if "--" not in arg_candidate:
            continue

        arg = arg_candidate[2:]
        # pull out the value of the argument if given
        if i + 1 <= len(args) - 1:
            if "--" not in args[i + 1]:
                value = args[i + 1]

            if arg is not None:
                parsed[arg] = value
        else:
            if arg is not None:
                parsed[arg] = value

    return parsed


def parse_grid_search(args):
    distributions = {}
    parsed = parse_args(args)

    for key, value in parsed.items():
        # TODO: Invest on doing a better parsing
        value = eval(value)
        if isinstance(value, list):
            value = {"distribution": "categorical", "params": {"choices": value}}
        distributions[key] = value
    return distributions


def parse_random_search(args):
    distributions = {}
    parsed = parse_args(args)

    for key, value in parsed.items():
        # TODO: Invest on doing a better parsing
        value = eval(value)
        if isinstance(value, list):
            if len(value) != 2:
                raise Exception(f"We are expecting low and high values for argument {key}. Found {value}.")
            low, high = value
            value = {"distribution": "uniform", "params": {"low": float(low), "high": float(high)}}
        else:
            raise Exception(f"The argument {key}: {value} wasn't parsed properly.")
        distributions[key] = value
    return distributions


class RunSweepCommand(ClientCommand):

    DESCRIPTION = "Command to run a Sweep or Trial"

    SUPPORTED_DISTRIBUTIONS = ("uniform", "log_uniform", "categorical")

    def run(self) -> None:
        parser = ArgumentParser()

        parser.add_argument("script_path", type=str, help="The path to the script to run.")
        parser.add_argument("--algorithm", default="grid_search", type=str, help="The search algorithm to use.")
        parser.add_argument("--total_experiments", default=None, type=int, help="The total number of experiments")
        parser.add_argument("--parallel_experiments", default=None, type=int, help="Number of trials to run.")
        parser.add_argument(
            "--requirements",
            default=[],
            type=lambda s: [v.replace(" ", "") for v in s.split(",")] if "," in s else s,
            help="List of requirements separated by a comma or requirements.txt filepath.",
        )
        parser.add_argument(
            "--cloud_compute",
            default="cpu",
            choices=["cpu", "cpu-small", "cpu-medium", "gpu", "gpu-fast", "gpu-fast-multi"],
            type=str,
            help="The machine to use in the cloud.",
        )
        parser.add_argument("--name", default=None, type=str, help="Configure your sweep name.")
        parser.add_argument(
            "--logger",
            default="tensorboard",
            choices=["tensorboard", "wandb"],
            type=str,
            help="The logger to use with your sweep.",
        )
        parser.add_argument(
            "--direction",
            default="minimize",
            choices=["minimize", "maximize"],
            type=str,
            help="In which direction to optimize.",
        )
        hparams, args = parser.parse_known_args()

        script_args = []

        total_experiments = hparams.total_experiments

        if hparams.algorithm == "grid_search":
            distributions = parse_grid_search(args)
            total_experiments = -1
        elif hparams.algorithm == "random_search":
            distributions = parse_random_search(args)
            if hparams.total_experiments is None:
                raise Exception("Please, specify the `total_experiments`.")
            if hparams.parallel_experiments is None:
                hparams.parallel_experiments = hparams.total_experiments
        else:
            distributions = parse_distributions(script_args, args)

        id = str(uuid4()).split("-")[0]
        name = hparams.name or f"{getuser()}-{id}"

        if not os.path.exists(hparams.script_path):
            raise ValueError(f"The provided script doesn't exist: {hparams.script_path}")

        if isinstance(hparams.requirements, str) and os.path.exists(hparams.requirements):
            with open(hparams.requirements, "r") as f:
                hparams.requirements = [line.replace("\n", "") for line in f.readlines()]

        repo = CustomLocalSourceCodeDir(path=Path(hparams.script_path).parent.resolve())
        # TODO: Resolve this bug.

        URL = self.state._state["vars"]["_layout"]["target"].replace("/root", "")
        if "localhost" in URL:
            URL = f"{APP_SERVER_HOST}:{APP_SERVER_PORT}"
        repo.package()
        repo.upload(url=f"{URL}/api/v1/upload_file/{name}")

        config = SweepConfig(
            sweep_id=name,
            script_path=hparams.script_path,
            n_trials=int(total_experiments),
            simultaneous_trials=hparams.parallel_experiments if isinstance(hparams.parallel_experiments, int) else 1,
            requirements=hparams.requirements,
            script_args=script_args,
            distributions=distributions,
            algorithm=hparams.algorithm,
            framework="pytorch_lightning",
            cloud_compute=hparams.cloud_compute,
            num_nodes=1,
            logger=hparams.logger,
            direction=hparams.direction,
            trials={},
        )
        response = self.invoke_handler(config=config)
        print(response)
