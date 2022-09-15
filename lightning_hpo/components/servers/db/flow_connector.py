from typing import Optional, Type

from sqlmodel import SQLModel

from lightning_hpo.components.servers.db.models import GeneralModel
from lightning_hpo.components.servers.db.work_db import general_delete, general_get, general_post, general_put


class FlowDatabaseConnector:
    def __init__(self, model: Type[SQLModel]):
        self.model = model

    def get(self, config: Optional[Type[SQLModel]] = None):
        cls = config if config else self.model
        return general_get(config=GeneralModel.from_cls(cls))

    def post(self, config: SQLModel):
        return general_post(GeneralModel.from_obj(config))

    def put(self, config: SQLModel):
        return general_put(GeneralModel.from_obj(config))

    def delete(self, config: SQLModel):
        return general_delete(GeneralModel.from_obj(config))
