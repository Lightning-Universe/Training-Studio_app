import sys
from subprocess import Popen

from lightning import BuildConfig, LightningWork


class DatabaseViz(LightningWork):
    def __init__(
        self,
        db_file_name: str = "database.db",
    ):
        super().__init__(parallel=True, cloud_build_config=BuildConfig(["sqlite-web"]))
        self.db_file_name = db_file_name

    def run(self):
        cmd = f"sqlite_web {self.db_file_name} -H {self.host} -p {self.port}"
        Popen(cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr).wait()

    def alive(self):
        """Hack: Returns whether the server is alive."""
        return self.url != ""
