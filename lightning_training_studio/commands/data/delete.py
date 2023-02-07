from argparse import ArgumentParser

from lightning.app.utilities.commands import ClientCommand
from sqlmodel import SQLModel


class DeleteDataConfig(SQLModel):
    name: str


class RemoveDatasetCommand(ClientCommand):
    description = """To delete a dataset association, note this doesn't delete the data, but only the reference."""

    def run(self) -> None:
        parser = ArgumentParser()

        parser.add_argument("--name", type=str, required=True, help="The name of the Data.")

        hparams = parser.parse_args()
        response = self.invoke_handler(config=DeleteDataConfig(name=hparams.name))
        print(response)
