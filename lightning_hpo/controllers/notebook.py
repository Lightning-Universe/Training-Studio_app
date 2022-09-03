from typing import List

from lightning_hpo.commands.notebook import RunNotebookCommand, RunNotebookConfig
from lightning_hpo.controllers.controller import Controller


class NotebookController(Controller):

    model = RunNotebookConfig

    def on_reconcile_start(self, configs: List[RunNotebookConfig]):
        # TODO: Implement the notebook creation. Have a look at the Tensorboard Controller.
        pass

    def run_notebook(self, config: RunNotebookConfig) -> str:
        self.db.post(config)
        return "The notebook has been created"

    def configure_commands(self) -> List:
        return [
            {"run notebook": RunNotebookCommand(self.run_notebook)},
            # TODO: stop notebook
        ]
