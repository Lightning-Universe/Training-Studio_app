from typing import List

from lightning import LightningFlow

from lightning_hpo.commands.notebook import CreateNotebookCommand, NotebookConfig


class NotebookController(LightningFlow):
    def __init__(self):
        super().__init__()

    def run(self, db_url: str):
        pass

    def notebook_handler(self, config: NotebookConfig) -> str:
        # resp = requests.post(self.db.url + "/sweep", data=config.json())
        return ""

    def configure_commands(self) -> List:
        return [
            {"create-notebook": CreateNotebookCommand(self.notebook_handler)},
        ]
