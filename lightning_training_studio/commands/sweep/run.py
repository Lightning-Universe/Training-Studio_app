import os
import re
from argparse import ArgumentParser
from ast import literal_eval
from getpass import getuser
from pathlib import Path
from typing import Dict, List, Optional, Union
from uuid import uuid4

import requests
from hydra.core.override_parser.overrides_parser import OverridesParser
from lightning.app.source_code import LocalSourceCodeDir
from lightning.app.source_code.uploader import FileUploader
from lightning.app.utilities.commands import ClientCommand
from pydantic import validator
from sqlalchemy import Column
from sqlmodel import Field, SQLModel

from lightning_training_studio.loggers import LoggerType
from lightning_training_studio.utilities.enum import Stage
from lightning_training_studio.utilities.utils import pydantic_column_type

RANGE_REGEX: re.Pattern = re.compile(r"^range\(([0-9]+,( ){0,1}){0,2}[0-9]+\)$")


class Distributions(SQLModel, table=False):
    distribution: str
    params: Dict[str, Union[float, int, str, List[float], List[str]]] = Field(
        sa_column=Column(pydantic_column_type(Dict[str, Union[float, int, List[float], List[str]]]))
    )


class ExperimentConfig(SQLModel, table=False):
    name: str
    best_model_score: Optional[float]
    monitor: Optional[str]
    best_model_path: Optional[str]
    last_model_path: Optional[str]
    stage: str = Stage.NOT_STARTED
    params: Dict[str, Union[float, int, str, List[float], List[str]]] = Field(
        sa_column=Column(pydantic_column_type(Dict[str, Union[float, int, List[float], List[str]]]))
    )
    exception: Optional[str]
    progress: Optional[float]
    total_parameters: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None

    @property
    def pruned(self) -> bool:
        return self.stage == Stage.PRUNED


class SweepConfig(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}

    sweep_id: str = Field(primary_key=True)
    script_path: str
    total_experiments: int
    parallel_experiments: int
    total_experiments_done: int = 0
    requirements: List[str] = Field(..., sa_column=Column(pydantic_column_type(List[str])))
    packages: List[str] = Field(..., sa_column=Column(pydantic_column_type(List[str])))
    script_args: List[str] = Field(..., sa_column=Column(pydantic_column_type(List[str])))
    algorithm: str
    distributions: Dict[str, Distributions] = Field(
        ..., sa_column=Column(pydantic_column_type(Dict[str, Distributions]))
    )
    logger_url: str = ""
    experiments: Dict[int, ExperimentConfig] = Field(
        ..., sa_column=Column(pydantic_column_type(Dict[int, ExperimentConfig]))
    )
    framework: str
    cloud_compute: str = "cpu"
    num_nodes: int = 1
    logger: str
    direction: str
    stage: str = Stage.NOT_STARTED
    desired_stage: str = Stage.RUNNING
    disk_size: int = 80
    pip_install_source: bool = False
    data: Dict[str, Optional[str]] = Field(..., sa_column=Column(pydantic_column_type(Dict[str, Optional[str]])))
    username: Optional[str] = None

    @property
    def num_experiments(self) -> int:
        return min(self.total_experiments_done + self.parallel_experiments, self.total_experiments)

    @property
    def hash(self) -> str:
        return self.sweep_id.split("-")[1]

    def is_tensorboard(self):
        return self.logger == LoggerType.TENSORBOARD.value

    @validator("data")
    def data_validator(cls, v, values, **kwargs):
        for _, mount_path in v.items():
            if mount_path is not None:
                if not mount_path.startswith("/"):
                    raise Exception("The `mount_path` needs to start with a leading slash (`/`)")
                elif not mount_path.endswith("/"):
                    raise Exception("The `mount_path` needs to end with in a trailing slash (`/`)")
        return v


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
        regex = "[0-9]+\.[0-9]+|[0-9]+"  # noqa W605
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
            if p.is_distribution(arg):
                distributions.update(p.parse(arg))
                is_distribution = True
                break
        if not is_distribution:
            script_args.append(arg)

    return {k: Distributions(distribution=x["distribution"], params=x["params"]) for k, x in distributions.items()}


def parse_args(args):
    parsed = {}
    last_arg = None

    # build a dict where key = arg, value = value of the arg or None if just a flag
    new_args = []
    for a in args:
        if "=" in a:
            new_args.extend(a.split("="))
        else:
            new_args.append(a)

    for arg_candidate in new_args:

        # only look at --keys
        if "--" not in arg_candidate:
            parsed[last_arg].append(arg_candidate)
        else:
            parsed[arg_candidate] = []
            last_arg = arg_candidate

    return {k: " ".join(v) for k, v in parsed.items()}


def parse_range_to_categorical(value: str):
    range_args = [literal_eval(val.strip()) for val in value.replace("range(", "").replace(")", "").split(",")]
    # Evaluates range expression to a list.
    value = list(range(*range_args))
    return {"distribution": "categorical", "params": {"choices": value}}


def _parse_list(value: str):
    try:
        value = literal_eval(value)
        if not isinstance(value, list):
            return None

        return value
    except Exception:
        pass


def parse_list_to_categorical(value: str):
    try:
        value = literal_eval(value)
        if not isinstance(value, list):
            return None

        return {"distribution": "categorical", "params": {"choices": value}}
    except Exception:
        pass


def parse_grid_search(script_args, args):
    distributions = {}
    parsed = parse_args(args)

    for key, value in parsed.items():
        expected_value = None
        if RANGE_REGEX.match(str(value)):
            expected_value = parse_range_to_categorical(value)
        else:
            expected_value = parse_list_to_categorical(value)
        if expected_value:
            distributions[key] = expected_value
        else:
            script_args.append(f"{key}={value}")
    return distributions


def parse_random_search(script_args, args):
    distributions = {}
    parsed = parse_args(args)

    for key, value in parsed.items():
        expected_value = None

        if RANGE_REGEX.match(value):
            expected_value = parse_range_to_categorical(value)
        else:
            expected_value = parse_list_to_categorical(value)
            if not expected_value:
                for p in [UniformDistributionParser, LogUniformDistributionParser, CategoricalDistributionParser]:
                    if p.is_distribution(value):
                        try:
                            expected_value = p.parse(f"{key}={value}")[key]
                            break
                        except Exception:
                            pass

        if expected_value:
            distributions[key] = expected_value
        else:
            script_args.append(f"{key}={value}")
    return distributions


def parse_hydra(script_args, args):
    distributions = {}
    parser = OverridesParser.create()
    parsed = parser.parse_overrides(args)
    for override in parsed:
        if override.is_sweep_override():
            key = override.get_key_element()
            values = override.sweep_string_iterator()
            distributions[key] = {"distribution": "categorical", "params": {"choices": list(values)}}
        else:
            script_args.append(override.input_line)
    return distributions


class RunSweepCommand(ClientCommand):

    description = """Run a sweep by providing a script, the cloud compute type and optional
                     data entries to be made available at a given path. Hyperparameters can be
                     provided as lists (`model.lr=\"[0.01, 0.1]\"`) or using distributions
                     (`model.lr=\"uniform(0.01, 0.1)\"`, `model.lr=\"log_uniform(0.01, 0.1)\"`).
                     Hydra multirun override syntax is also supported."""
    requirements = ["traitlets", "lightning_training_studio"]
    SUPPORTED_DISTRIBUTIONS = ("uniform", "log_uniform", "categorical")

    def run(self) -> None:
        parser = ArgumentParser()

        parser.add_argument("script_path", type=str, help="The path to the script to run.")
        parser.add_argument(
            "--algorithm",
            default="grid_search",
            type=str,
            help="The search algorithm to use.",
            choices=["grid_search", "random_search", "bayesian"],
        )
        parser.add_argument("--total_experiments", default=None, type=int, help="The total number of experiments")
        parser.add_argument("--parallel_experiments", default=None, type=int, help="Number of experiments to run.")
        parser.add_argument(
            "--requirements",
            nargs="+",
            default=[],
            help="List of requirements separated by a comma or requirements.txt filepath.",
        )
        parser.add_argument(
            "--packages",
            nargs="+",
            default=[],
            help="List of system packages to be installed via apt install, separated by a comma.",
        )
        parser.add_argument(
            "--cloud_compute",
            default="cpu-small",
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
        parser.add_argument(
            "--framework",
            default="pytorch_lightning",
            choices=["pytorch_lightning", "base"],
            type=str,
            help="Which framework you are using.",
        )
        parser.add_argument(
            "--num_nodes",
            default=1,
            type=int,
            help="The number of nodes.",
        )
        parser.add_argument(
            "--disk_size",
            default=10,
            type=int,
            help="The disk size in Gigabytes.",
        )
        parser.add_argument(
            "--data",
            nargs="+",
            default=[],
            help="Provide a list of Data (and optionally the mount_path in the format `<name>:<mount_path>`) to mount to the experiments.",
        )
        parser.add_argument(
            "--syntax",
            default="default",
            choices=["default", "hydra"],
            type=str,
            help="Syntax for sweep parameters at the CLI.",
        )
        parser.add_argument(
            "--pip-install-source",
            default=False,
            action="store_true",
            help="Run `pip install -e .` on the uploaded source before running",
        )

        hparams, args = parser.parse_known_args()

        if hparams.framework != "pytorch_lightning" and hparams.num_nodes > 1:
            raise ValueError("Multi Node is support only for PyTorch Lightning.")

        script_args = []

        total_experiments = hparams.total_experiments

        if hparams.syntax == "hydra":
            distributions = parse_hydra(script_args, args)
            total_experiments = -1
        elif hparams.algorithm == "grid_search":
            distributions = parse_grid_search(script_args, args)
            total_experiments = -1
        elif hparams.algorithm == "random_search":
            distributions = parse_random_search(script_args, args)
            if not distributions:
                total_experiments = 1
            elif distributions and hparams.total_experiments is None:
                raise Exception("Please, specify the `total_experiments`.")
            else:
                total_experiments = hparams.total_experiments
            if hparams.parallel_experiments is None:
                hparams.parallel_experiments = total_experiments
        else:
            distributions = parse_distributions(script_args, args)

        name = hparams.name or str(uuid4()).split("-")[-1][:7]

        if not os.path.exists(hparams.script_path):
            raise ValueError(f"The provided script doesn't exist: {hparams.script_path}")

        if not os.path.exists(hparams.script_path):
            raise FileNotFoundError(f"The provided script doesn't exist: {hparams.script_path}")

        if len(hparams.requirements) == 1 and Path(hparams.requirements[0]).resolve().exists():
            requirements_path = Path(hparams.requirements[0]).resolve()
            with open(requirements_path, "r") as f:
                hparams.requirements = [line.replace("\n", "") for line in f.readlines() if line.strip()]

        repo = CustomLocalSourceCodeDir(path=Path(hparams.script_path).parent.resolve())
        repo.package()
        repo.upload(url=f"{self.app_url}/api/v1/upload_file/{name}")

        data_split = [data.split(":") if ":" in data else (data, None) for data in hparams.data]
        data = {data[0]: data[1] for data in data_split}

        config = SweepConfig(
            sweep_id=name,
            script_path=hparams.script_path,
            total_experiments=int(total_experiments),
            parallel_experiments=hparams.parallel_experiments if isinstance(hparams.parallel_experiments, int) else 1,
            requirements=hparams.requirements,
            packages=hparams.packages,
            script_args=script_args,
            distributions=distributions,
            algorithm=hparams.algorithm,
            framework=hparams.framework,
            cloud_compute=hparams.cloud_compute,
            num_nodes=hparams.num_nodes,
            logger=hparams.logger,
            direction=hparams.direction,
            experiments={},
            disk_size=hparams.disk_size,
            pip_install_source=hparams.pip_install_source,
            data=data,
            username=getuser(),
        )
        response = self.invoke_handler(config=config)
        print(response)
