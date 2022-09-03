import os
import re
from argparse import ArgumentParser
from getpass import getuser
from pathlib import Path
from typing import Dict, List, Optional, Union
from uuid import uuid4

import requests
from lightning.app.source_code import LocalSourceCodeDir
from lightning.app.source_code.uploader import FileUploader
from lightning.app.utilities.commands import ClientCommand
from sqlalchemy import Column
from sqlmodel import Field, SQLModel

from lightning_hpo.utilities.enum import Status
from lightning_hpo.utilities.utils import pydantic_column_type


class Params(SQLModel, table=False):
    params: Dict[str, Union[float, int, List[float], List[str]]] = Field(
        sa_column=Column(pydantic_column_type(Dict[str, Union[float, int, List[float], List[str]]]))
    )


class Distributions(SQLModel, table=False):
    distribution: str
    params: Params = Field(sa_column=Column(pydantic_column_type(Params)))


class TrialConfig(SQLModel, table=False):
    best_model_score: Optional[float]
    monitor: Optional[str]
    best_model_path: Optional[str]
    status: str = Status.NOT_STARTED
    params: Params = Field(sa_column=Column(pydantic_column_type(Params)))
    exception: Optional[str]

    @property
    def pruned(self) -> bool:
        return self.status == Status.PRUNED


class SweepConfig(SQLModel, table=True):
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    sweep_id: str
    script_path: str
    n_trials: int
    simultaneous_trials: int
    trials_done: int = 0
    requirements: List[str] = Field(..., sa_column=Column(pydantic_column_type(List[str])))
    script_args: List[str] = Field(..., sa_column=Column(pydantic_column_type(List[str])))
    distributions: Dict[str, Distributions] = Field(
        ..., sa_column=Column(pydantic_column_type(Dict[str, Distributions]))
    )
    url: Optional[str] = None
    trials: Dict[int, TrialConfig] = Field(..., sa_column=Column(pydantic_column_type(Dict[int, TrialConfig])))
    framework: str
    cloud_compute: str
    num_nodes: int = 1
    logger: str
    direction: str
    status: str = Status.NOT_STARTED

    @property
    def num_trials(self) -> int:
        return self.trials_done + self.simultaneous_trials

    @property
    def username(self) -> str:
        return self.sweep_id.split("-")[0]

    @property
    def hash(self) -> str:
        return self.sweep_id.split("-")[1]


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
        resp = s.put(url, files={"file": data})
        return resp.status_code


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


class RunSweepCommand(ClientCommand):

    DESCRIPTION = "Command to run a Sweep or Trial"

    SUPPORTED_DISTRIBUTIONS = ("uniform", "log_uniform", "categorical")

    def run(self) -> None:
        parser = ArgumentParser()
        parser.add_argument("script_path", type=str, help="The path to the script to run.")
        parser.add_argument("--n_trials", type=int, help="Number of trials to run.")
        parser.add_argument("--simultaneous_trials", default=1, type=int, help="Number of trials to run.")
        parser.add_argument("--requirements", nargs="+", default=[], help="Requirements file.")
        parser.add_argument("--framework", default="pytorch_lightning", type=str, help="The framework you are using.")
        parser.add_argument("--cloud_compute", default="cpu", type=str, help="The machine to use in the cloud.")
        parser.add_argument("--sweep_id", default=None, type=str, help="The sweep you want to run upon.")
        parser.add_argument("--num_nodes", default=1, type=int, help="The number of nodes to train upon.")
        parser.add_argument("--logger", default="streamlit", type=str, help="The logger to use with your sweep.")
        parser.add_argument(
            "--direction",
            default="minimize",
            choices=["minimize", "maximize"],
            type=str,
            help="In which direction to optimize.",
        )
        hparams, args = parser.parse_known_args()

        if any("=" not in arg for arg in args):
            raise Exception("Please, provide the arguments as follows --x=y")

        script_args = []
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

        id = str(uuid4()).split("-")[0]
        sweep_id = hparams.sweep_id or f"{getuser()}-{id}"

        if not os.path.exists(hparams.script_path):
            raise Exception("The provided script doesn't exists.")

        repo = CustomLocalSourceCodeDir(path=Path(hparams.script_path).parent.resolve())
        # TODO: Resolve this bug.
        url = self.state.file_server._state["vars"]["_url"]
        repo.package()
        repo.upload(url=f"{url}/uploadfile/{sweep_id}")

        distributions = {
            k: Distributions(distribution=x["distribution"], params=Params(params=x["params"]))
            for k, x in distributions.items()
        }

        config = SweepConfig(
            sweep_id=sweep_id,
            script_path=hparams.script_path,
            n_trials=int(hparams.n_trials),
            simultaneous_trials=hparams.simultaneous_trials,
            requirements=hparams.requirements,
            script_args=script_args,
            distributions=distributions,
            framework=hparams.framework,
            cloud_compute=hparams.cloud_compute,
            num_nodes=hparams.num_nodes,
            logger=hparams.logger,
            direction=hparams.direction,
            trials={},
        )
        response = self.invoke_handler(config=config)
        print(response)
