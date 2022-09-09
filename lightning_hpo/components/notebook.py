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
        self.has_updated = False
        self._process: Optional[Popen] = None

    def run(self, *args, **kwargs):
        super().run()
        self.has_updated = True

    # TODO: Cleanup exit mechanism in lightning.
    def on_exit(self):
        if _is_work_context():
            assert self._process
            self._process.kill()
        else:
            self._config.status = Status.NOT_STARTED

    @property
    def updates(self):
        if self.url != "" and self.has_updated:
            self._config.status = Status.RUNNING
            self._config.url = self.url
            self.has_updated = False
            return [self._config]
        return []
