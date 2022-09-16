from argparse import ArgumentParser

from lightning.app.utilities.commands import ClientCommand
from pydantic import BaseModel


class StopNotebookConfig(BaseModel):
    notebook_name: str


class StopNotebookCommand(ClientCommand):
    def run(self) -> None:
        parser = ArgumentParser()
        parser.add_argument("--name", required=True, help="The name of your notebook to be stopped.")
        hparams, _ = parser.parse_known_args()
        response = self.invoke_handler(config=StopNotebookConfig(notebook_name=hparams.name))
        print(response)
