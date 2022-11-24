from argparse import ArgumentParser

from lightning.app.utilities.commands import ClientCommand
from sqlmodel import SQLModel


class DeleteDataConfig(SQLModel):
    name: str


class DeleteDataCommand(ClientCommand):

    description = """Delete a data association. Note that this will not delete the data itself,
                     it will only make it unavailable to experiments and sweeps."""

    def run(self) -> None:
        parser = ArgumentParser()

        parser.add_argument("--name", type=str, required=True, help="The name of the Data.")

        hparams = parser.parse_args()
        response = self.invoke_handler(config=DeleteDataConfig(name=hparams.name))
        print(response)
