from typing import List

from lightning_hpo.commands.notebook.run import NotebookConfig, RunNotebookCommand
from lightning_hpo.commands.notebook.show import ShowNotebookCommand
from lightning_hpo.commands.notebook.stop import StopNotebookCommand, StopNotebookConfig
from lightning_hpo.components.notebook import JupyterLab
from lightning_hpo.controllers.controller import Controller
from lightning_hpo.utilities.enum import Status


class NotebookController(Controller):

    model = NotebookConfig

    def on_reconcile_start(self, configs: List[NotebookConfig]):
        for config in configs:
            if config.name not in self.r and config.desired_state == Status.RUNNING:
                self.r[config.name] = JupyterLab(
                    kernel="python",
                    config=config,
                )

    def run_notebook(self, config: NotebookConfig) -> str:
        if config.name in self.r:
            return f"The notebook `{config.name}` already exists."
        self.db.post(config)
        return f"The notebook `{config.name}` has been created."

    def stop_notebook(self, config: StopNotebookConfig) -> str:
        matched_notebook = None
        for notebook_name, notebook in self.r.items():
            if notebook_name == config.name:
                matched_notebook = notebook

        if matched_notebook:
            if matched_notebook.config["status"] != Status.STOPPED:
                notebook: JupyterLab = self.r[config.name]
                notebook.stop()
                notebook.config["desired_state"] = notebook.config["status"] = Status.STOPPED
                self.db.put(NotebookConfig(**notebook.config))
                return f"The notebook `{config.name}` has been stopped."
            return f"The notebook `{config.name}` is already stopped."
        return f"The notebook `{config.name}` doesn't exist."

    def show_notebook(self):
        if self.db_url:
            return self.db.get()
        return []

    def configure_commands(self) -> List:
        return [
            {"run notebook": RunNotebookCommand(self.run_notebook)},
            {"stop notebook": StopNotebookCommand(self.stop_notebook)},
            {"show notebooks": ShowNotebookCommand(self.show_notebook)},
        ]
