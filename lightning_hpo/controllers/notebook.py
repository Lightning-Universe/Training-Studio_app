from typing import List

import requests
from lightning import LightningFlow

from lightning_hpo.commands.notebook import CreateNotebookCommand, NotebookConfig
from lightning_hpo.components.servers.db.models import GeneralModel


class NotebookController(LightningFlow):
    def __init__(self):
        super().__init__()
        self.db_url = None

    def run(self, db_url: str):
        self.db_url = db_url

    def notebook_handler(self, config: NotebookConfig) -> str:
        assert self.db_url
        resp = requests.post(self.db_url + "/general/", data=GeneralModel.from_obj(config).json())
        assert resp.status_code == 200
        return "The notebook has been created"

    def configure_commands(self) -> List:
        return [
            {"create-notebook": CreateNotebookCommand(self.notebook_handler)},
        ]
