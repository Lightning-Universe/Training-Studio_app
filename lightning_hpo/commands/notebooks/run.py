from argparse import ArgumentParser
from getpass import getuser
from typing import List, Optional
from uuid import uuid4

from lightning.app.utilities.commands import ClientCommand
from sqlalchemy import Column
from sqlmodel import Field, SQLModel

from lightning_hpo.utilities.enum import Status
from lightning_hpo.utilities.utils import pydantic_column_type


class NotebookConfig(SQLModel, table=True):

    __table_args__ = {"extend_existing": True}

    id: Optional[str] = Field(default=None, primary_key=True)
    name: str
    requirements: List[str] = Field(..., sa_column=Column(pydantic_column_type(List[str])))
    cloud_compute: str
    status: str = Status.NOT_STARTED
    desired_state: str = Status.RUNNING


class RunNotebookCommand(ClientCommand):
    def run(self) -> None:
        parser = ArgumentParser()

        parser.add_argument("name", help="The name of your notebook to run.")
        parser.add_argument("--requirements", nargs="+", default=[], help="Requirements file.")
        parser.add_argument("--cloud_compute", default="cpu", type=str, help="The machine to use in the cloud.")

        hparams, _ = parser.parse_known_args()
        id = str(uuid4()).split("-")[0]

        config = NotebookConfig(
            id=f"{getuser()}-{id}",
            name=hparams.name,
            requirements=hparams.requirements,
            cloud_compute=hparams.cloud_compute,
        )
        response = self.invoke_handler(config=config)
        print(response)
