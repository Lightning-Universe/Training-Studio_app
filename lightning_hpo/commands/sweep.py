import json
import os
import re
import sys
from argparse import ArgumentParser
from getpass import getuser
from pathlib import Path
from typing import Dict, Generic, List, Optional, TypeVar
from uuid import uuid4

import requests
from fastapi.encoders import jsonable_encoder
from lightning.app.source_code import LocalSourceCodeDir
from lightning.app.source_code.uploader import FileUploader
from lightning.app.utilities.commands import ClientCommand
from pydantic import parse_obj_as
from pydantic.main import ModelMetaclass
from sqlalchemy import Column
from sqlmodel import Field, JSON, SQLModel, TypeDecorator

T = TypeVar("T")


# Taken from https://github.com/tiangolo/sqlmodel/issues/63#issuecomment-1081555082
def pydantic_column_type(pydantic_type):
    class PydanticJSONType(TypeDecorator, Generic[T]):
        impl = JSON()

        def __init__(
            self,
            json_encoder=json,
        ):
            self.json_encoder = json_encoder
            super(PydanticJSONType, self).__init__()

        def bind_processor(self, dialect):
            impl_processor = self.impl.bind_processor(dialect)
            dumps = self.json_encoder.dumps
            if impl_processor:

                def process(value: T):
                    if value is not None:
                        if isinstance(pydantic_type, ModelMetaclass):
                            # This allows to assign non-InDB models and if they're
                            # compatible, they're directly parsed into the InDB
                            # representation, thus hiding the implementation in the
                            # background. However, the InDB model will still be returned
                            value_to_dump = pydantic_type.from_orm(value)
                        else:
                            value_to_dump = value
                        value = jsonable_encoder(value_to_dump)
                    return impl_processor(value)

            else:

                def process(value):
                    if isinstance(pydantic_type, ModelMetaclass):
                        # This allows to assign non-InDB models and if they're
                        # compatible, they're directly parsed into the InDB
                        # representation, thus hiding the implementation in the
                        # background. However, the InDB model will still be returned
                        value_to_dump = pydantic_type.from_orm(value)
                    else:
                        value_to_dump = value
                    value = dumps(jsonable_encoder(value_to_dump))
                    return value

            return process

        def result_processor(self, dialect, coltype) -> T:
            impl_processor = self.impl.result_processor(dialect, coltype)
            if impl_processor:

                def process(value):
                    value = impl_processor(value)
                    if value is None:
                        return None

                    data = value
                    # Explicitly use the generic directly, not type(T)
                    full_obj = parse_obj_as(pydantic_type, data)
                    return full_obj

            else:

                def process(value):
                    if value is None:
                        return None

                    # Explicitly use the generic directly, not type(T)
                    full_obj = parse_obj_as(pydantic_type, value)
                    return full_obj

            return process

        def compare_values(self, x, y):
            return x == y

    return PydanticJSONType


class Params(SQLModel, table=False):
    params: Dict[str, str] = Field(sa_column=Column(pydantic_column_type(Dict[str, str])))


class Distributions(SQLModel, table=False):
    distribution: str
    params: Params = Field(sa_column=Column(pydantic_column_type(Params)))


class SweepConfig(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sweep_id: str
    script_path: str
    n_trials: int
    simultaneous_trials: int
    num_trials: int = 0
    requirements: List[str] = Field(..., sa_column=Column(pydantic_column_type(List[str])))
    script_args: List[str] = Field(..., sa_column=Column(pydantic_column_type(List[str])))
    distributions: Dict[str, Distributions] = Field(
        ..., sa_column=Column(pydantic_column_type(Dict[str, Distributions]))
    )
    framework: str
    cloud_compute: str
    num_nodes: int = 1
    logger: str
    direction: str


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


class SweepCommand(ClientCommand):

    SUPPORTED_DISTRIBUTIONS = ("uniform", "log_uniform", "categorical")

    def run(self) -> None:
        sys.argv = sys.argv[1:]
        script_path = sys.argv[0]

        parser = ArgumentParser()
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

        if not os.path.exists(script_path):
            raise Exception("The provided script doesn't exists.")

        repo = CustomLocalSourceCodeDir(path=Path(script_path).parent.resolve())
        url = self.state.sweeper.file_server._state["vars"]["_url"]
        repo.package()
        repo.upload(url=f"{url}/uploadfile/{sweep_id}")

        distributions = {
            k: Distributions(distribution=x["distribution"], params=Params(params=x["params"]))
            for k, x in distributions.items()
        }

        config = SweepConfig(
            sweep_id=sweep_id,
            script_path=script_path,
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
        )
        response = self.invoke_handler(config=config)
        print(response)
