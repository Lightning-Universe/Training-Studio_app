from argparse import ArgumentParser

from lightning.app.utilities.commands import ClientCommand
from sqlmodel import SQLModel


class DeleteMountConfig(SQLModel):
    name: str


class DeleteMountCommand(ClientCommand):

    DESCRIPTION = "Delete a Mount."

    def run(self) -> None:
        parser = ArgumentParser()

        parser.add_argument("--name", type=str, required=True, help="The associated name of the Mount.")

        hparams = parser.parse_args()
        response = self.invoke_handler(config=DeleteMountConfig(name=hparams.name))
        print(response)
