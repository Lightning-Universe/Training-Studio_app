import logging
import os
import subprocess
import sys
from typing import Optional

from lightning import CloudCompute, LightningWork
from lightning.app.storage import Path

logger = logging.getLogger(__name__)


class JupyterLabWork(LightningWork):
    def __init__(self, cloud_compute: Optional[CloudCompute] = None):
        super().__init__(cloud_compute=cloud_compute, parallel=True)
        self.pid = None
        self.token = None
        self.exit_code = None
        self.storage = None

    def run(self):
        self.storage = Path(".")

        jupyter_notebook_config_path = Path.home() / ".jupyter/jupyter_notebook_config.py"

        if os.path.exists(jupyter_notebook_config_path):
            os.remove(jupyter_notebook_config_path)

        with subprocess.Popen(
            f"{sys.executable} -m notebook --generate-config".split(" "),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=0,
            close_fds=True,
        ) as proc:
            self.pid = proc.pid

            self.exit_code = proc.wait()
            if self.exit_code != 0:
                raise Exception(self.exit_code)

        with open(jupyter_notebook_config_path, "a") as f:
            f.write(
                """c.NotebookApp.tornado_settings = {'headers': {'Content-Security-Policy': "frame-ancestors * 'self' "}}"""  # noqa E501
            )

        with open(f"jupyter_lab_{self.port}", "w") as f:
            proc = subprocess.Popen(
                f"{sys.executable} -m jupyter lab --ip {self.host} --port {self.port} --no-browser --config={jupyter_notebook_config_path}".split(
                    " "
                ),
                bufsize=0,
                close_fds=True,
                stdout=f,
                stderr=f,
            )

        with open(f"jupyter_lab_{self.port}") as f:
            while True:
                for line in f.readlines():
                    if "lab?token=" in line:
                        self.token = line.split("lab?token=")[-1]
                        proc.wait()

    @property
    def url(self):
        if not self.token:
            return ""
        if self._future_url:
            return f"{self._future_url}/lab?token={self.token}"
        else:
            return f"http://{self.host}:{self.port}/lab?token={self.token}"
