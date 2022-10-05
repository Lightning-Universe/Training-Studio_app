import os
from argparse import ArgumentParser

from lightning.app.utilities.commands import ClientCommand
from sqlmodel import Field, SQLModel


class DriveConfig(SQLModel, table=True):

    __table_args__ = {"extend_existing": True}

    name: str = Field(primary_key=True)
    source: str
    mount_path: str


class CreateDriveCommand(ClientCommand):

    DESCRIPTION = "Command to create a Drive"

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
