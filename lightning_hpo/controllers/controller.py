from abc import abstractmethod
from typing import List, Optional, Type

import requests
from lightning import LightningFlow
from lightning.app.storage import Drive
from lightning.app.structures import Dict
from sqlmodel import SQLModel

from lightning_hpo.components.servers.db.models import GeneralModel


class Controller(LightningFlow):

    model: Type[SQLModel]
    model_id: Optional[str] = None

    def __init__(self, drive: Optional[Drive] = None):
        super().__init__()
        self.db_url = None
        self.resources = Dict()
        self.drive = drive

    def run(self, db_url: str, configs: Optional[List[Type[SQLModel]]] = None):
        self.db_url = db_url

        # 1: Read from the database and generate the works accordingly.
        # TODO: Improve the schedule API.
        if self.schedule("* * * * * 0,5,10,15,20,25,30,35,40,45,50,55"):
            resp = requests.get(self.db_url + "/general/", data=GeneralModel.from_cls(self.model).json())
            assert resp.status_code == 200
            db_configs = [self.model(**data) for data in resp.json()]
            if configs:
                db_configs += db_configs
            if db_configs:
                self.on_reconcile_start(db_configs)

        # 2: Iterate over the sweeps and collect updates
        updates = []
        for resource in self.resources.values():
            resource.run()
            updates.extend(resource.updates)

        if not updates:
            return

        # 3: Reconcile sweep on end
        for update in updates:
            resp = requests.put(self.db_url + "/general/", data=GeneralModel.from_obj(update, id=self.model_id).json())
            assert resp.status_code == 200

        self.on_reconcile_end(updates)

    @abstractmethod
    def on_reconcile_start(self, configs):
        """Override with your start reconciliation mechanism."""

    @abstractmethod
    def on_reconcile_end(self, updates):
        """Override with your end reconciliation mechanism."""
