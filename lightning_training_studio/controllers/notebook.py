import urllib.parse
from typing import List, Optional

from lightning_training_studio.commands.notebook.run import NotebookConfig, RunNotebookCommand
from lightning_training_studio.commands.notebook.show import ShowNotebookCommand
from lightning_training_studio.commands.notebook.stop import StopNotebookCommand, StopNotebookConfig
from lightning_training_studio.components.notebook import JupyterLab
from lightning_training_studio.controllers.controller import Controller
from lightning_training_studio.utilities.enum import Stage


class NotebookController(Controller):

    model = NotebookConfig

    def on_reconcile_start(self, configs: List[NotebookConfig]):
        for config in configs:
            work_name = urllib.parse.quote_plus(config.notebook_name)
            if work_name in self.r and self.r[work_name].status.stage == Stage.STOPPED:
                self.r[work_name].stage = Stage.STOPPED

            if config.desired_stage == Stage.RUNNING and config.stage not in [Stage.PENDING, Stage.RUNNING]:
                self.r[work_name] = JupyterLab(
                    kernel="python",
                    config=config,
                )
                self.r[work_name].stage = Stage.PENDING
            elif all(
                [
                    work_name in self.r,
                    config.desired_stage == Stage.STOPPED,
                    config.stage not in [Stage.STOPPING, Stage.STOPPED],
                ]
            ):
                self.r[work_name].stop()
                self.r[work_name]._url = ""
                self.r[work_name].stage = Stage.STOPPING

    def run_notebook(self, config: NotebookConfig) -> str:
        matched_notebook: Optional[NotebookConfig] = None
        for existing_config in self.db.select_all():
            if existing_config.notebook_name == config.notebook_name:
                matched_notebook = existing_config

        if matched_notebook:
            if matched_notebook.stage == Stage.RUNNING and matched_notebook.desired_stage == Stage.RUNNING:
                return f"The notebook `{config.notebook_name}` is already running."

            config.desired_stage = Stage.RUNNING
            # Update config in the database
            self.db.update(config)
            return f"The notebook `{config.notebook_name}` has been updated."

        self.db.insert(config)
        return f"The notebook `{config.notebook_name}` has been created."

    def stop_notebook(self, config: StopNotebookConfig) -> str:
        matched_notebook = None
        for notebook in self.r.values():
            if notebook.notebook_name == config.notebook_name:
                matched_notebook = notebook

        if matched_notebook:
            if matched_notebook.desired_stage != Stage.STOPPED:
                matched_notebook.desired_stage = Stage.STOPPED
                self.db.update(matched_notebook.collect_model())
                return f"The notebook `{config.notebook_name}` has been stopped."
            return f"The notebook `{config.notebook_name}` is already stopped."
        names = [notebook.notebook_name for notebook in self.r.values()]
        if not names:
            return "You don't have any notebooks. Create a notebook with `lightning run notebook --name=my_name`."
        return f"The notebook `{config.notebook_name}` doesn't exist. Found the following notebooks: {names}."

    def show_notebook(self):
        if self.db_url:
            return self.db.select_all()
        return []

    def configure_commands(self) -> List:
        return [
            {"run notebook": RunNotebookCommand(self.run_notebook)},
            {"stop notebook": StopNotebookCommand(self.stop_notebook)},
            {"show notebooks": ShowNotebookCommand(self.show_notebook)},
        ]
