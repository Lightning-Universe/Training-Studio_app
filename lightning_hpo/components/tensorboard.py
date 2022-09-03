from subprocess import Popen

from lightning import LightningWork
from lightning.app.storage import Drive


class Tensorboard(LightningWork):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self, drive: Drive):
        Popen(
            f"tensorboard --logdir='{drive.root}' --host {self.host} --port {self.port}",
            shell=True,
        )
