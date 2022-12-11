import os
from pathlib import Path
from subprocess import Popen
from uuid import uuid4

from lightning import LightningWork
from lightning.app.storage import Drive
from lightning.app.storage.path import _filesystem

from lightning_training_studio.commands.tensorboard.stop import TensorboardConfig
from lightning_training_studio.controllers.controller import ControllerResource
from lightning_training_studio.utilities.enum import Stage


class Tensorboard(LightningWork, ControllerResource):

    model = TensorboardConfig

    def __init__(self, *args, drive: Drive, config: TensorboardConfig, **kwargs):
        super().__init__(*args, parallel=True, **kwargs)
        self.drive = drive
        self.sweep_id = config.sweep_id
        self.shared_folder = config.shared_folder
        self.stage = config.stage
        self.desired_stage = config.desired_stage
        self.config = config.dict()

    def run(self):
        use_localhost = "LIGHTNING_APP_STATE_URL" not in os.environ

        local_folder = f"./tensorboard_logs/{uuid4()}"

        os.makedirs(local_folder, exist_ok=True)

        # Note: Used tensorboard built-in sync methods but it doesn't seem to work.
        extras = "--reload_interval 1 --reload_multifile True"
        cmd = f"tensorboard --logdir={local_folder} --host {self.host} --port {self.port} {extras}"
        self._process = Popen(cmd, shell=True, env=os.environ)

        self.stage = Stage.RUNNING
        fs = _filesystem()
        root_folder = str(self.drive.drive_root)

        while True:
            fs.invalidate_cache()
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
                    fs.get(source_path, str(Path(target_path).resolve()))

    def on_exit(self):
        assert self._process
        self._process.kill()

    def on_collect_model(self, model_dict):
        model_dict["url"] = self.url
