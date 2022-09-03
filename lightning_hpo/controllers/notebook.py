from typing import List

import requests

from lightning_hpo.commands.notebook import RunNotebookCommand, RunNotebookConfig
from lightning_hpo.components.servers.db.models import GeneralModel
from lightning_hpo.controllers.controller import Controller


class NotebookController(Controller):

    model = RunNotebookConfig

    def on_reconcile_start(self, configs: List[RunNotebookConfig]):
        # TODO: Implement the notebook creation. Have a look at the Tensorboard Controller.
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
