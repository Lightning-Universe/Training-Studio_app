import os
import time
from pathlib import Path
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
        use_localhost = "LIGHTNING_APP_STATE_URL" not in os.environ

        local_folder = f"./tensorboard_logs/{uuid4()}"

        os.makedirs(local_folder, exist_ok=True)

        # Note: Used tensorboard built-in sync methods but it doesn't seem to work.
        cmd = f"tensorboard --logdir={local_folder} --host {self.host} --port {self.port}"
        self._process = Popen(cmd, shell=True, env=os.environ)

        self.has_updated = True
        fs = filesystem()
        root_folder = str(self.drive.drive_root)

        while True:
            fs.invalidate_cache()
            if fs.exists(root_folder):
                if use_localhost:
                    for dir, _, files in fs.walk(root_folder):
                        for filepath in files:
                            if "events.out.tfevents" not in filepath:
                                continue
                            source_path = os.path.join(dir, filepath)
                            target_path = os.path.join(dir, filepath).replace(root_folder, local_folder)
                            if use_localhost:
                                parent = Path(target_path).resolve().parent
                                if not parent.exists():
                                    parent.mkdir(exist_ok=True, parents=True)
                            fs.cp(source_path, str(Path(target_path).resolve()))
                else:
                    # TODO: Debug the cloud support to support the above strategy
                    # to copy only the logs.
                    fs.invalidate_cache()
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
