import time
from subprocess import Popen
from typing import Optional

from lai_jupyter import JupyterLab
from lightning import CloudCompute

from lightning_training_studio.commands.notebook.run import NotebookConfig
from lightning_training_studio.controllers.controller import ControllerResource
from lightning_training_studio.utilities.enum import Stage


class JupyterLab(JupyterLab, ControllerResource):

    model = NotebookConfig

    def __init__(self, config: NotebookConfig, **kwargs):
        super().__init__(cloud_compute=CloudCompute(name=config.cloud_compute), **kwargs)
        self._process: Optional[Popen] = None

        reqs = self.cloud_build_config.requirements
        self.cloud_build_config.requirements = (reqs if reqs else []) + config.requirements

        self.notebook_name = config.notebook_name
        self.requirements = config.requirements
        self.desired_stage = config.desired_stage
        self.stage = config.stage
        self.start_time = config.start_time

    def run(self, *args, **kwargs):
        super().run()
        self.stage = Stage.RUNNING
        self.start_time = time.time()

    def on_exit(self):
        assert self._process
        self._process.kill()

    def on_collect_model(self, model_dict):
        model_dict["cloud_compute"] = self.cloud_compute.name
        if self.stage == Stage.RUNNING and self.url:
            model_dict["url"] = self.url
        else:
            model_dict.pop("url", None)
