from subprocess import Popen
from typing import Optional

from lightning import CloudCompute
from lightning.app.utilities.component import _is_work_context
from lit_jupyter import JupyterLab

from lightning_hpo.commands.notebook.run import NotebookConfig
from lightning_hpo.controllers.controller import ControllerResource


class JupyterLab(JupyterLab, ControllerResource):

    model = NotebookConfig

    def __init__(self, config: NotebookConfig, **kwargs):
        super().__init__(cloud_compute=CloudCompute(name=config.cloud_compute), **kwargs)
        self._process: Optional[Popen] = None

        self.notebook_name = config.notebook_name
        self.requirements = config.requirements
        self.cloud_compute = config.cloud_compute
        self.desired_stage = config.desired_stage
        self.stage = config.stage

    def run(self, *args, **kwargs):
        super().run()

    # TODO: Cleanup exit mechanism in lightning.
    def on_exit(self):
        if _is_work_context():
            assert self._process
            self._process.kill()

    def on_collect_model(self, model_dict):
        if self.url:
            model_dict["url"] = self.url
        else:
            model_dict["url"] = None
