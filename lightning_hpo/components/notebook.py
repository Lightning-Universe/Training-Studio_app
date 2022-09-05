from subprocess import Popen
from typing import Optional

from lightning.app.utilities.component import _is_work_context
from lit_jupyter import JupyterLab

from lightning_hpo.commands.notebook.run import NotebookConfig
from lightning_hpo.utilities.enum import Status


class JupyterLab(JupyterLab):
    def __init__(self, *args, config: NotebookConfig, **kwargs):
        super().__init__(*args, **kwargs)
        self._config = config
        self.ready = False
        self.has_updated = False
        self._process: Optional[Popen] = None

    def run(self, *args, **kwargs):
        super().run()
        self.ready = True
        self.has_updated = True

    # TODO: Cleanup exit mechanism in lightning.
    def on_exit(self):
        if _is_work_context():
            assert self._process
            self._process.kill()

    @property
    def updates(self):
        if self.has_updated and self.ready:
            self._config.status = Status.RUNNING
            self.has_updated = False
            return [self._config]
        return []
