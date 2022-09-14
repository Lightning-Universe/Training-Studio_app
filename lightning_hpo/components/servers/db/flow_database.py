from typing import List, Type

from lightning import LightningFlow
from sqlmodel import SQLModel

from lightning_hpo.components.servers.db.server import create_engine


class FlowDatabase(LightningFlow):
    def __init__(
        self,
        models: List[Type[SQLModel]],
        db_file_name: str = "database.db",
        debug: bool = False,
    ):
        super().__init__()
        create_engine(db_file_name, models, debug)
        self.db_url = "flow"

    def alive(self):
        return True
