from argparse import ArgumentParser

from lightning.app.utilities.commands import ClientCommand
from sqlmodel import SQLModel


class DeleteDriveConfig(SQLModel):
    name: str


class DeleteDriveCommand(ClientCommand):

    description = "Delete a Drive."

    def run(self) -> None:
        parser = ArgumentParser()

        parser.add_argument("--name", type=str, required=True, help="The associated name of the drive.")

        hparams = parser.parse_args()
        response = self.invoke_handler(config=DeleteDriveConfig(name=hparams.name))
        print(response)
