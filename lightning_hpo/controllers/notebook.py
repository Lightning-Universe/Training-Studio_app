from typing import List

from lightning_hpo.commands.notebook.run import NotebookConfig, RunNotebookCommand
from lightning_hpo.commands.notebook.show import ShowNotebookCommand
from lightning_hpo.commands.notebook.stop import StopNotebookCommand, StopNotebookConfig
from lightning_hpo.components.notebook import JupyterLab
from lightning_hpo.controllers.controller import Controller
from lightning_hpo.utilities.enum import Stage


class NotebookController(Controller):

    model = NotebookConfig

    def on_reconcile_start(self, configs: List[NotebookConfig]):
        for config in configs:
            if config.desired_stage == Stage.RUNNING:
                # If the work is already there and status is pending then we don't need to recreate it
                if config.notebook_name in self.r and self.r[config.notebook_name].stage in (
                    Stage.PENDING,
                    Stage.RUNNING,
                ):
                    return
                self.r[config.notebook_name] = JupyterLab(
                    kernel="python",
                    config=config,
                )
                # TODO: Without this the work keeps getting recreated
                self.r[config.notebook_name].stage = Stage.PENDING

    def run_notebook(self, config: NotebookConfig) -> str:
        configs = self.db.get()
        if any(existing_config.notebook_name == config.notebook_name for existing_config in configs):
            # Update config in the database
            config.stage = Stage.PENDING
            self.db.put(config)
            return f"The notebook `{config.notebook_name}` has been updated."

        self.db.post(config)
        return f"The notebook `{config.notebook_name}` has been created."

    def stop_notebook(self, config: StopNotebookConfig) -> str:
        matched_notebook = None
        for notebook_name, notebook in self.r.items():
            if notebook_name == config.name:
                matched_notebook = notebook

        if matched_notebook:
            model: NotebookConfig = notebook.collect_model()
            if model.stage != Stage.STOPPED:
                notebook: JupyterLab = self.r[config.name]
                notebook.stop()
                model = notebook.collect_model()
                model.desired_stage = Stage.STOPPED
                model.stage = Stage.STOPPING
                self.db.put(model)
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
