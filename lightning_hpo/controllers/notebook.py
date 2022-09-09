from typing import List

from lightning import CloudCompute

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
            if config.desired_state == Status.RUNNING:
                # If the work is already there and status is pending then we don't need to recreate it
                if config.name in self.r and self.r[config.name]._config.status in (Status.PENDING, Status.RUNNING):
                    return
                self.r[config.name] = JupyterLab(
                    kernel="python",
                    cloud_compute=CloudCompute(name=config.cloud_compute),
                    config=config,
                )
                # TODO: Without this the work keeps getting recreated
                self.r[config.name]._config.status = Status.PENDING

    def run_notebook(self, config: NotebookConfig) -> str:
        configs = self.db.get()
        if any(existing_config.name == config.name for existing_config in configs):
            # Update config in the database
            config.status = Status.PENDING
            self.db.put(config)
            return f"The notebook `{config.name}` has been updated."

        self.db.post(config)
        return f"The notebook `{config.name}` has been created."

    def stop_notebook(self, config: StopNotebookConfig) -> str:
        matched_notebook = None
        for notebook_name, notebook in self.r.items():
            if notebook_name == config.name:
                matched_notebook = notebook

        if matched_notebook:
            if matched_notebook._config.status != Status.STOPPED:
                notebook: JupyterLab = self.r[config.name]
                notebook.stop()
                notebook._config.desired_state = notebook._config.status = Status.STOPPED
                self.db.put(notebook._config)
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
