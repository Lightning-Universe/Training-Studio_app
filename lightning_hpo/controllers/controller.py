from abc import abstractmethod
from typing import List, Optional, Type

from lightning import LightningFlow
from lightning.app.storage import Drive
from lightning.app.structures import Dict
from sqlmodel import SQLModel

from lightning_hpo.components.servers.db import DatabaseConnector


class Controller(LightningFlow):

    model: Type[SQLModel]
    model_id: Optional[str] = None

    def __init__(self, drive: Optional[Drive] = None):
        super().__init__()
        self.db_url = None
        self.resources = Dict()
        self.drive = drive
        self._database = None

    def run(self, db_url: str, configs: Optional[List[Type[SQLModel]]] = None):
        self.db_url = db_url

        # TODO: Resolve scheduling. It seems only the last one is activated somehow in the cloud.
        # TODO: Improve the schedule API.
        # 1: Read from the database and generate the works accordingly.
        # if self.schedule("* * * * * 0,5,10,15,20,25,30,35,40,45,50,55"):
        db_configs = self.db.get()
        if configs:
            db_configs += db_configs
        if db_configs:
            self.on_reconcile_start(db_configs)

        # 2: Iterate over the resources and collect updates
        updates = []
        for resource in self.resources.values():
            resource.run()
            updates.extend(resource.updates)

        if not updates:
            return

        # 3: Reconcile resources on end
        for update in updates:
            self.db.put(update)

        self.on_reconcile_end(updates)

    @property
    def db(self) -> DatabaseConnector:
        if self._database is None:
            assert self.db_url is not None
            self._database = DatabaseConnector(self.model, self.db_url + "/general/", self.model_id or "id")
        return self._database

    @abstractmethod
    def on_reconcile_start(self, configs):
        """Override with your start reconciliation mechanism."""

    @abstractmethod
    def on_reconcile_end(self, updates):
        """Override with your end reconciliation mechanism."""
