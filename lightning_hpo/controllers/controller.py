import typing
from abc import abstractmethod
from typing import Any, List, Optional, Type

from lightning import LightningFlow
from lightning.app.storage import Drive
from lightning.app.structures import Dict
from sqlmodel import SQLModel

from lightning_hpo.components.servers.db import DatabaseConnector
from lightning_hpo.utilities.enum import Status
from lightning_hpo.utilities.utils import get_primary_key


class ControllerResource:

    config: typing.Dict[str, Any]


class Controller(LightningFlow):

    model: Type[SQLModel]

    def __init__(self, drive: Optional[Drive] = None):
        super().__init__()
        self.db_url = None
        self.r = Dict()
        self.drive = drive
        self._database = None
        self.ready = False

    def run(self, db_url: str, configs: Optional[List[Type[SQLModel]]] = None):
        self.db_url = db_url

        # TODO: Resolve scheduling. It seems only the last one is activated somehow in the cloud.
        # TODO: Improve the schedule API.
        # 1: Read from the database and generate the works accordingly.
        # if self.schedule("* * * * * 0,5,10,15,20,25,30,35,40,45,50,55"):
        db_configs = self.db.get()
        if not self.ready:
            for config in db_configs:
                config.status = Status.NOT_STARTED
                self.db.put(config)
            self.ready = True

        if configs:
            db_configs += db_configs
        if db_configs:
            self.on_reconcile_start(db_configs)

        # 2: Iterate over the.r and collect updates
        configs = []
        for resource in self.r.values():
            resource.run()
            configs.append(self.model(**resource.config))

        if not configs:
            return

        # 3: Reconcile.r on end
        primary_key = get_primary_key(self.model)
        db_configs = {getattr(config, primary_key): config for config in db_configs}
        for config in configs:
            db_config = db_configs[getattr(config, primary_key)]
            if config != db_config:
                self.db.put(config)

        self.on_reconcile_end(configs)

    @property
    def db(self) -> DatabaseConnector:
        if self._database is None:
            assert self.db_url is not None
            self._database = DatabaseConnector(self.model, self.db_url + "/general/")
        return self._database

    @abstractmethod
    def on_reconcile_start(self, configs):
        """Override with your start reconciliation mechanism."""

    @abstractmethod
    def on_reconcile_end(self, updates):
        """Override with your end reconciliation mechanism."""
