from subprocess import Popen
from typing import Optional

from lightning import CloudCompute
from lightning.app.utilities.component import _is_work_context
from lit_jupyter import JupyterLab

from lightning_hpo.commands.notebook.run import NotebookConfig
from lightning_hpo.controllers.controller import ControllerResource
from lightning_hpo.utilities.enum import Status


class JupyterLab(JupyterLab, ControllerResource):

    model = NotebookConfig

    def __init__(self, config: NotebookConfig, **kwargs):
        super().__init__(cloud_compute=CloudCompute(name=config.cloud_compute), **kwargs)

        self.config = config.dict()

        self._process: Optional[Popen] = None

    def run(self, *args, **kwargs):
        super().run()
        self.config["url"] = self.url
        self.config["status"] = Status.RUNNING

    # TODO: Cleanup exit mechanism in lightning.
    def on_exit(self):
        if _is_work_context():
            assert self._process
            self._process.kill()
        else:
            self.config["status"] = Status.NOT_STARTED
