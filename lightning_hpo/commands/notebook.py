from argparse import ArgumentParser
from getpass import getuser
from typing import List, Optional
from uuid import uuid4

from lightning.app.utilities.commands import ClientCommand
from sqlalchemy import Column
from sqlmodel import Field, SQLModel

from lightning_hpo.utilities.enum import Status
from lightning_hpo.utilities.utils import pydantic_column_type


class NotebookConfig(SQLModel, table=False):
    id: Optional[str] = Field(default=None, primary_key=True)
    name: str
    requirements: List[str] = Field(..., sa_column=Column(pydantic_column_type(List[str])))
    cloud_compute: str
    status: str = Status.NOT_STARTED


class CreateNotebookCommand(ClientCommand):
    def run(self) -> None:
        parser = ArgumentParser()

        parser.add_argument("--name", required=True, help="The name of your notebook")
        parser.add_argument("--requirements", nargs="+", default=[], help="Requirements file.")
        parser.add_argument("--cloud_compute", default="cpu", type=str, help="The machine to use in the cloud.")

        hparams, _ = parser.parse_known_args()
        id = str(uuid4()).split("-")[0]

        config = NotebookConfig(
            id=f"{getuser()}-{id}",
            name=hparams.name,
            requirements=hparams.requirements,
            cloud_compute=hparams.cloud_compute,
            status=Status.NOT_STARTED,
        )
        response = self.invoke_handler(config=config)
        print(response)
