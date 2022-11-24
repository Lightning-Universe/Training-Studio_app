from argparse import ArgumentParser

from lightning.app.utilities.commands import ClientCommand
from pydantic import BaseModel


class DeleteExperimentConfig(BaseModel):
    name: str


class DeleteExperimentCommand(ClientCommand):

    description = "Delete an experiment. Note that artifacts will still be available after the operation."

    def run(self) -> None:
        parser = ArgumentParser()
        parser.add_argument("--name", type=str, required=True, help="The associated experiment `name` to delete.")
        hparams = parser.parse_args()
        response = self.invoke_handler(config=DeleteExperimentConfig(name=hparams.name))
        print(response)
