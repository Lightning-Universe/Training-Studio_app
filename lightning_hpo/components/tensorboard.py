from subprocess import Popen

from lightning import LightningWork
from lightning.app.storage import Drive


class Tensorboard(LightningWork):
    def __init__(self, *args, drive: Drive, **kwargs):
        super().__init__(*args, **kwargs)
        self.drive = drive
        self.drive.component_name = "logs"

    def run(self):
        self.drive.component_name = "logs"
        cmd = f"tensorboard --logdir='{self.drive.root}' --host {self.host} --port {self.port}"
        print(cmd)
        self._process = Popen(cmd, shell=True)

    def on_exception(self, exception):
        self._process.kill()
        super().on_exception(exception)

    @property
    def updates(self):
        return []
