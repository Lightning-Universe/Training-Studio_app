from typing import List

from lightning import CloudCompute

from lightning_hpo.commands.notebooks.run import NotebookConfig, RunNotebookCommand
from lightning_hpo.commands.notebooks.show import ShowNotebookCommand
from lightning_hpo.commands.notebooks.stop import StopNotebookCommand, StopNotebookConfig
from lightning_hpo.components.notebook import JupyterLab
from lightning_hpo.controllers.controller import Controller
from lightning_hpo.utilities.enum import Status


class NotebookController(Controller):

    model = NotebookConfig

    def on_reconcile_start(self, configs: List[NotebookConfig]):
        for config in configs:
            if config.name not in self.resources and config.desired_state == Status.RUNNING:
                self.resources[config.name] = JupyterLab(
                    cloud_compute=CloudCompute(name=config.cloud_compute),
                    config=config,
                )

    def run_notebook(self, config: NotebookConfig) -> str:
        if config.name in self.resources:
            return f"The notebook `{config.name}` already exists."
        self.db.post(config)
        return f"The notebook `{config.name}` has been created."

    def stop_notebook(self, config: StopNotebookConfig) -> str:
        matched_notebook = None
        notebooks: List[NotebookConfig] = self.db.get()
        for notebook in notebooks:
            if notebook.name == config.name:
                matched_notebook = notebook

        if matched_notebook:
            if matched_notebook.name in self.resources:
                notebook: JupyterLab = self.resources[config.name]
                notebook.stop()
                notebook._config.desired_state = notebook._config.status = Status.STOPPED
                self.db.put(notebook._config)
                return f"The notebook `{config.name}` has been stopped."
            return f"The notebook `{config.name}` is stopped."
        return f"The notebook `{config.name}` doesn't exist."

    def show_notebook(self):
        return self.db.get()

    def configure_commands(self) -> List:
        return [
            {"run notebook": RunNotebookCommand(self.run_notebook)},
            {"stop notebook": StopNotebookCommand(self.stop_notebook)},
            {"show notebooks": ShowNotebookCommand(self.show_notebook)},
        ]
