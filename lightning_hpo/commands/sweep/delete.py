from argparse import ArgumentParser

from lightning.app.utilities.commands import ClientCommand
from pydantic import BaseModel


class DeleteSweepConfig(BaseModel):
    sweep_id: str


class DeleteSweepCommand(ClientCommand):

    DESCRIPTION = "Command to delete a Sweep"

    def run(self) -> None:
        parser = ArgumentParser()
        parser.add_argument("sweep_id", type=str, help="The associated `sweep_id` to delete.")
        hparams = parser.parse_args()
        response = self.invoke_handler(config=DeleteSweepConfig(sweep_id=hparams.sweep_id))
        print(response)
