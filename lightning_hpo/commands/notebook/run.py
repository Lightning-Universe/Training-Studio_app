from argparse import ArgumentParser
from typing import List

from lightning.app.utilities.commands import ClientCommand
from sqlalchemy import Column
from sqlmodel import Field, SQLModel

from lightning_hpo.utilities.enum import Stage
from lightning_hpo.utilities.utils import pydantic_column_type


class NotebookConfig(SQLModel, table=True):

    __table_args__ = {"extend_existing": True}

    notebook_name: str = Field(primary_key=True)
    requirements: List[str] = Field(..., sa_column=Column(pydantic_column_type(List[str])))
    cloud_compute: str
    drive: str
    drive_mount_dir: str
    stage: str = Stage.NOT_STARTED
    desired_stage: str = Stage.RUNNING
    url: str = ""
    start_time: float = -1


class RunNotebookCommand(ClientCommand):
    def run(self) -> None:
        parser = ArgumentParser()

        parser.add_argument("--name", help="The name of your notebook to run.")
        parser.add_argument("--requirements", nargs="+", default=[], help="Requirements file.")
        parser.add_argument("--cloud_compute", default="cpu", type=str, help="The machine to use in the cloud.")
        parser.add_argument(
            "--drive", default="", type=str, help="The path to a public S3 bucket to mount in the notebook."
        )
        parser.add_argument(
            "--drive_mount_dir", default="data/", type=str, help="The path where the drive will be mounted."
        )

        hparams, _ = parser.parse_known_args()

        config = NotebookConfig(
            notebook_name=hparams.name,
            requirements=hparams.requirements,
            cloud_compute=hparams.cloud_compute,
            drive=hparams.drive,
            drive_mount_dir=hparams.drive_mount_dir,
        )
        response = self.invoke_handler(config=config)
        print(response)
