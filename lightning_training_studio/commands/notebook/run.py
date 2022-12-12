import os
from argparse import ArgumentParser
from getpass import getuser
from typing import List
from uuid import uuid4

from lightning.app.utilities.commands import ClientCommand
from sqlalchemy import Column
from sqlmodel import Field, SQLModel

from lightning_training_studio.utilities.enum import Stage
from lightning_training_studio.utilities.utils import pydantic_column_type


class NotebookConfig(SQLModel, table=True):

    __table_args__ = {"extend_existing": True}

    notebook_name: str = Field(primary_key=True)
    requirements: List[str] = Field(..., sa_column=Column(pydantic_column_type(List[str])))
    cloud_compute: str
    stage: str = Stage.NOT_STARTED
    desired_stage: str = Stage.RUNNING
    url: str = ""
    start_time: float = -1


class RunNotebookCommand(ClientCommand):
    def run(self) -> None:
        parser = ArgumentParser()

        parser.add_argument("--name", default=None, help="The name of your notebook to run.")
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

        hparams, _ = parser.parse_known_args()

        if isinstance(hparams.requirements, str) and os.path.exists(hparams.requirements):
            with open(hparams.requirements, "r") as f:
                hparams.requirements = [line.replace("\n", "") for line in f.readlines()]

        id = str(uuid4()).split("-")[0]
        notebook_name = hparams.name or f"{getuser()}-{id}"

        config = NotebookConfig(
            notebook_name=notebook_name,
            requirements=hparams.requirements,
            cloud_compute=hparams.cloud_compute,
        )
        response = self.invoke_handler(config=config)
        print(response)
