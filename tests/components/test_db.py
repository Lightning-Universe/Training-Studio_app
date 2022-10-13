import os
from time import sleep
from uuid import uuid4

from lightning import LightningApp, LightningFlow
from lightning.app.runners import MultiProcessRuntime
from sqlmodel import Field, SQLModel

from lightning_hpo.components.servers.db.work_connector import DatabaseConnector
from lightning_hpo.components.servers.db.work_db import Database


class Example(SQLModel, table=True):
    name: str = Field(primary_key=True)


def test_work_database():

    id = str(uuid4()).split("-")[0]

    class Flow(LightningFlow):
        def __init__(self, restart=False):
            super().__init__()
            self.db = Database(db_file_name=id, models=[Example])
            self._client = None
            self.restart = restart

        def run(self):
            self.db.run()

            if not self.db.alive():
                return
            elif not self._client:
                self._client = DatabaseConnector(Example, self.db.db_url + "/general/")

            if not self.restart:
                self._client.post(Example(name="echo"))
                self._exit()
            else:
                assert os.path.exists(id)
                assert len(self._client.get()) == 1
                self._exit()

    app = LightningApp(Flow())
    MultiProcessRuntime(app).dispatch()

    # Note: Waiting for SIGTERM signal to be handled
    sleep(2)

    os.remove(id)

    app = LightningApp(Flow(restart=True))
    MultiProcessRuntime(app).dispatch()

    # Note: Waiting for SIGTERM signal to be handled
    sleep(2)

    os.remove(id)
