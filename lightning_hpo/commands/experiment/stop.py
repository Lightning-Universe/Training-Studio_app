from argparse import ArgumentParser

from lightning.app.utilities.commands import ClientCommand
from pydantic import BaseModel


class StopExperimentConfig(BaseModel):
    name: str


class StopExperimentCommand(ClientCommand):

    description = "Stop an experiment. Note that currently experiments cannot be resumed."

    def run(self) -> None:
        parser = ArgumentParser()
        parser.add_argument("--name", type=str, required=True, help="The associated `experiment_name` to stop.")
        hparams = parser.parse_args()
        response = self.invoke_handler(config=StopExperimentConfig(name=hparams.name))
        print(response)
