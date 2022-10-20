import os
from argparse import ArgumentParser

from lightning.app.utilities.commands import ClientCommand
from pydantic import validator
from sqlmodel import Field, SQLModel


class DriveConfig(SQLModel, table=True):

    __table_args__ = {"extend_existing": True}

    name: str = Field(primary_key=True)
    source: str
    mount_path: str

    @validator("source")
    def source_validator(cls, v):
        if not v.startswith("s3://"):
            raise Exception('The `source` needs to start with "s3://"')
        elif not v.endswith("/"):
            raise Exception("The `source` needs to end with in a trailing slash (`/`)")
        return v

    @validator("mount_path")
    def mount_path_validator(cls, v, values, **kwargs):
        if not v.startswith("/"):
            raise Exception("The `mount_path` needs to start with in a trailing slash (`/`)")
        elif not v.endswith("/"):
            raise Exception("The `mount_path` needs to end with in a trailing slash (`/`)")
        return v


class CreateDriveCommand(ClientCommand):

    description = "Create a Drive."

    def run(self) -> None:
        parser = ArgumentParser()

        parser.add_argument("--name", type=str, required=True, help="The associated name of the drive.")
        parser.add_argument("--source", type=str, required=True, help="The associated S3 URL of the drive.")
        parser.add_argument(
            "--mount_path", type=str, default=None, help="Where the drive should be mounted to the works"
        )

        hparams = parser.parse_args()
        mount_path = hparams.mount_path if hparams.mount_path else os.path.join("./drive", hparams.name)
        response = self.invoke_handler(
            config=DriveConfig(name=hparams.name, source=hparams.source, mount_path=mount_path)
        )
        print(response)
