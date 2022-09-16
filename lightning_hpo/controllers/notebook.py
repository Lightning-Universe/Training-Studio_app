from typing import List, Optional

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
            if config.notebook_name in self.r and self.r[config.notebook_name].status.stage == Stage.STOPPED:
                self.r[config.notebook_name].stage = Stage.STOPPED

            if config.desired_stage == Stage.RUNNING and config.stage not in [Stage.PENDING, Stage.RUNNING]:
                self.r[config.notebook_name] = JupyterLab(
                    kernel="python",
                    config=config,
                )
                self.r[config.notebook_name].stage = Stage.PENDING
            elif all(
                [
                    config.notebook_name in self.r,
                    config.desired_stage == Stage.STOPPED,
                    config.stage not in [Stage.STOPPING, Stage.STOPPED],
                ]
            ):
                self.r[config.notebook_name].stop()
                self.r[config.notebook_name]._url = ""
                self.r[config.notebook_name].stage = Stage.STOPPING

    def run_notebook(self, config: NotebookConfig) -> str:
        matched_notebook: Optional[NotebookConfig] = None
        for existing_config in self.db.get():
            if existing_config.notebook_name == config.notebook_name:
                matched_notebook = existing_config

        if matched_notebook:
            if matched_notebook.stage == Stage.RUNNING and matched_notebook.desired_stage == Stage.RUNNING:
                return f"The notebook `{config.notebook_name}` is already running."

            config.desired_stage = Stage.RUNNING
            # Update config in the database
            self.db.put(config)
            return f"The notebook `{config.notebook_name}` has been updated."

        self.db.post(config)
        return f"The notebook `{config.notebook_name}` has been created."

    def stop_notebook(self, config: StopNotebookConfig) -> str:
        matched_notebook = None
        for notebook_name, notebook in self.r.items():
            if notebook_name == config.notebook_name:
                matched_notebook = notebook

        if matched_notebook:
            model: NotebookConfig = matched_notebook.collect_model()
            if model.desired_stage != Stage.STOPPED:
                notebook: JupyterLab = self.r[config.notebook_name]
                notebook.desired_stage = Stage.STOPPED
                self.db.put(notebook.collect_model())
                return f"The notebook `{config.notebook_name}` has been stopped."
            return f"The notebook `{config.notebook_name}` is already stopped."
        return f"The notebook `{config.notebook_name}` doesn't exist. Found the following notebooks: {list(self.r)}."

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
