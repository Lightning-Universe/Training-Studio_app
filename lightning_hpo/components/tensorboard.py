import os
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
        cmd = f"tensorboard --logdir='s3://{self.drive.root}' --host {self.host} --port {self.port}"

        os.environ["S3_ENDPOINT"] = os.getenv("LIGHTNING_BUCKET_ENDPOINT_URL", "")
        os.environ["S3_VERIFY_SSL"] = "0"
        os.environ["S3_USE_HTTPS"] = "0"
        # TODO: What is LAI platform
        os.environ["AWS_REGION"] = "eu-west-1"

        print(cmd, os.environ)

        self._process = Popen(cmd, shell=True, env=os.environ)

    def on_exception(self, exception):
        self._process.kill()
        super().on_exception(exception)

    @property
    def updates(self):
        return []
