import os
import time
from subprocess import Popen
from uuid import uuid4

from lightning import LightningWork
from lightning.app.storage import Drive
from lightning.app.storage.path import filesystem
from lightning.app.utilities.component import _is_work_context

from lightning_hpo.commands.tensorboard.stop import TensorboardConfig
from lightning_hpo.utilities.enum import Status


class Tensorboard(LightningWork):
    def __init__(self, *args, drive: Drive, sleep: int = 5, config: TensorboardConfig, **kwargs):
        super().__init__(*args, parallel=True, **kwargs)
        self.drive = drive
        self.sleep = sleep
        self.has_updated = False
        self._config = config

    def run(self):
        local_folder = f"./tensorboard_logs/{uuid4()}"

        os.makedirs(local_folder, exist_ok=True)

        # Note: Used tensorboard built-in sync methods but it doesn't seem to work.
        cmd = f"tensorboard --logdir={local_folder} --host {self.host} --port {self.port}"
        self._process = Popen(cmd, shell=True, env=os.environ)

        self.has_updated = True

        fs = filesystem()

        while True:
            fs.invalidate_cache()
            folder = str(self.drive.drive_root)
            if fs.exists(folder):
                fs.get(str(self.drive.drive_root), local_folder, recursive=True)
            time.sleep(self.sleep)

    def on_exit(self):
        if _is_work_context():
            assert self._process
            self._process.kill()
        else:
            self._config.status = Status.NOT_STARTED

    @property
    def updates(self):
        if self.has_updated:
            self._config.status = Status.RUNNING
            self._config.url = self.url
            self.has_updated = False
            return [self._config]
        return []
