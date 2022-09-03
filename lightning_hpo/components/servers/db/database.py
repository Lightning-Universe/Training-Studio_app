from typing import Optional, Type

import requests
from sqlmodel import SQLModel

from lightning_hpo.components.servers.db.models import GeneralModel


class Database:
    def __init__(self, model: Type[SQLModel], db_url: str, model_id: Optional[str] = None):
        self.model = model
        self.db_url = db_url
        self.model_id = model_id

    def get(self, config: Optional[Type[SQLModel]] = None):
        cls = config if config else self.model
        resp = requests.get(self.db_url + "/general/", data=GeneralModel.from_cls(cls).json())
        assert resp.status_code == 200
        return [cls(**data) for data in resp.json()]

    def post(self, config: SQLModel, model_id: Optional[str] = None):
        resp = requests.post(
            self.db_url + "/general/", data=GeneralModel.from_obj(config, id=model_id or self.model_id).json()
        )
        assert resp.status_code == 200

    def put(self, config: SQLModel, model_id: Optional[str] = None):
        resp = requests.put(
            self.db_url + "/general/", data=GeneralModel.from_obj(config, id=self.model_id or self.model_id).json()
        )
        assert resp.status_code == 200

    def delete(self, config: SQLModel, model_id: Optional[str] = None):
        resp = requests.delete(
            self.db_url + "/general/", data=GeneralModel.from_obj(config, id=self.model_id or self.model_id).json()
        )
        assert resp.status_code == 200
