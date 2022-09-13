import os
import pathlib
import time
import uuid
from subprocess import Popen
from typing import Optional

from lightning import CloudCompute
from lightning.app.storage import Drive
from lightning.app.utilities.component import _is_work_context
from lit_jupyter import JupyterLab

from lightning_hpo.commands.notebook.run import NotebookConfig
from lightning_hpo.controllers.controller import ControllerResource
from lightning_hpo.utilities.enum import Stage


class JupyterLab(JupyterLab, ControllerResource):

    model = NotebookConfig

    def __init__(self, config: NotebookConfig, **kwargs):
        super().__init__(cloud_compute=CloudCompute(name=config.cloud_compute), **kwargs)
        self._process: Optional[Popen] = None

        self.notebook_name = config.notebook_name
        self.requirements = config.requirements
        self.drive = config.drive
        self.drive_mount_dir = config.drive_mount_dir
        self.desired_stage = config.desired_stage
        self.stage = config.stage
        self.start_time = config.start_time

        if config.drive:
            os.makedirs(pathlib.Path(config.drive_mount_dir).resolve())
            setattr(self, uuid.uuid4().hex, Drive(config.drive, root_folder=config.drive_mount_dir))

    def run(self, *args, **kwargs):
        print(os.listdir(self.drive_mount_dir))
        super().run()
        self.stage = Stage.RUNNING
        self.start_time = time.time()

    # TODO: Cleanup exit mechanism in lightning.
    def on_exit(self):
        if _is_work_context():
            assert self._process
            self._process.kill()

    def on_collect_model(self, model_dict):
        model_dict["cloud_compute"] = self.cloud_compute.name
        if self.url and self.stage == Stage.RUNNING:
            model_dict["url"] = self.url
        else:
            model_dict["url"] = None
