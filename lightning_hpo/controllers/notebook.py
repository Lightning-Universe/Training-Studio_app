from typing import List

import requests
from lightning import LightningFlow

from lightning_hpo.commands.notebook import RunNotebookCommand, RunNotebookConfig
from lightning_hpo.components.servers.db.models import GeneralModel


class NotebookController(LightningFlow):
    def __init__(self):
        super().__init__()
        self.db_url = None

    def run(self, db_url: str):
        self.db_url = db_url

        # TODO: Implement the notebook reconciliation

    def reconcile_notebooks(self):
        resp = requests.get(self.db_url + "/general/", data=GeneralModel.from_cls(RunNotebookConfig).json())
        assert resp.status_code == 200
        notebooks = [RunNotebookConfig(**notebook) for notebook in resp.json()]
        for notebook in notebooks:
            # TODO: Implement the thingy there.
            pass

    def run_notebook(self, config: RunNotebookConfig) -> str:
        assert self.db_url
        resp = requests.post(self.db_url + "/general/", data=GeneralModel.from_obj(config).json())
        assert resp.status_code == 200
        return "The notebook has been created"

    def configure_commands(self) -> List:
        return [
            {"run notebook": RunNotebookCommand(self.run_notebook)},
            # TODO: stop notebook
        ]
