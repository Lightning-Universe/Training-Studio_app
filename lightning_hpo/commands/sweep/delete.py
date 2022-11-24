from argparse import ArgumentParser

from lightning.app.utilities.commands import ClientCommand
from pydantic import BaseModel


class DeleteSweepConfig(BaseModel):
    name: str


class DeleteSweepCommand(ClientCommand):

    description = "Delete a sweep. Note that artifacts will still be available after the operation."

    def run(self) -> None:
        parser = ArgumentParser()
        parser.add_argument("--name", type=str, required=True, help="The associated `sweep_id` to delete.")
        hparams = parser.parse_args()
        response = self.invoke_handler(config=DeleteSweepConfig(name=hparams.name))
        print(response)
