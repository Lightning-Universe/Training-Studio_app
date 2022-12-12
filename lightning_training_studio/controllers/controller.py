from abc import abstractmethod
from typing import List, Optional, Type

from lightning import LightningFlow
from lightning.app.components.database import DatabaseClient
from lightning.app.storage import Drive
from lightning.app.structures import Dict
from sqlmodel import SQLModel

from lightning_training_studio.utilities.enum import Stage
from lightning_training_studio.utilities.utils import get_primary_key


class ControllerResource:

    model: Type[SQLModel]

    def on_collect_model(self, model_dict):
        """Override to add the missing elements to the model_dict."""

    def collect_model(self):
        keys = list(self.model.__fields__)
        model_dict = {key: getattr(self, key) for key in keys if key in self._state}
        self.on_collect_model(model_dict)
        return self.model.parse_obj(model_dict)


class Controller(LightningFlow):

    model: Type[SQLModel]

    def __init__(self, drive: Optional[Drive] = None):
        super().__init__()
        self.db_url = None
        self._token = None
        self.r = Dict()
        self.drive = drive
        self._db_client = None
        self.has_setup = False

    def run(self, db_url: str, token: str, configs: Optional[List[Type[SQLModel]]] = None):
        self.db_url = db_url
        self._token = token

        # TODO: Resolve scheduling. It seems only the last one is activated somehow in the cloud.
        # TODO: Improve the schedule API.
        # 1: Read from the database and generate the works accordingly.
        # if self.schedule("* * * * * 0,5,10,15,20,25,30,35,40,45,50,55"):
        db_configs = self.db.select_all()
        if not self.has_setup:
            for config in db_configs:
                config.stage = Stage.NOT_STARTED
                self.db.update(config)
            self.has_setup = True

        if configs:
            db_configs += db_configs
        if db_configs:
            self.on_reconcile_start(db_configs)

        # 2: Iterate over the.r and collect updates
        configs = []
        for resource in self.r.values():
            resource.run()
            configs.append(resource.collect_model())

        if not configs:
            return

        # 3: Reconciler on end
        primary_key = get_primary_key(self.model)
        db_configs = {getattr(config, primary_key): config for config in db_configs}
        for config in configs:
            db_config = db_configs[getattr(config, primary_key)]
            if config.dict() != db_config.dict():
                self.db.update(config)

        self.on_reconcile_end(configs)

    @property
    def db(self) -> DatabaseClient:
        if self._db_client is None:
            assert self.db_url is not None
            self._db_client = DatabaseClient(self.db_url, self._token, model=self.model)
        return self._db_client

    @abstractmethod
    def on_reconcile_start(self, configs):
        """Override with your start reconciliation mechanism."""

    @abstractmethod
    def on_reconcile_end(self, updates):
        """Override with your end reconciliation mechanism."""
