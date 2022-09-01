from argparse import ArgumentParser

from lightning.app.utilities.commands import ClientCommand
from pydantic import BaseModel


class StopSweep(BaseModel):
    sweep_id: str


class StopSweepCommand(ClientCommand):
    def run(self) -> None:
        parser = ArgumentParser()
        parser.add_argument("sweep_id", type=str, help="The associated `sweep_id` to stop.")
        hparams = parser.parse_args()
        response = self.invoke_handler(config=StopSweep(sweep_id=hparams.sweep_id))
        print(response)
