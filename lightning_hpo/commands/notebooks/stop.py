from argparse import ArgumentParser
from typing import Optional

from lightning.app.utilities.commands import ClientCommand
from pydantic import BaseModel


class StopNotebookConfig(BaseModel):
    name: Optional[str]


class StopNotebookCommand(ClientCommand):
    def run(self) -> None:
        parser = ArgumentParser()
        parser.add_argument("name", help="The name of your notebook to be stopped.")
        hparams, _ = parser.parse_known_args()
        response = self.invoke_handler(config=StopNotebookConfig(name=hparams.name))
        print(response)
