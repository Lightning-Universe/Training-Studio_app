from argparse import ArgumentParser

from lightning.app.utilities.commands import ClientCommand
from pydantic import BaseModel


class StopSweepConfig(BaseModel):
    sweep_id: str


class StopSweepCommand(ClientCommand):

    description = "Stop a Sweep."

    def run(self) -> None:
        parser = ArgumentParser()
        parser.add_argument("--name", type=str, help="The associated `sweep_id` to stop.")
        hparams = parser.parse_args()
        response = self.invoke_handler(config=StopSweepConfig(sweep_id=hparams.name))
        print(response)
