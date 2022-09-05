from typing import Optional, Type

import requests
from requests import Session
from requests.adapters import HTTPAdapter
from sqlmodel import SQLModel
from urllib3.util.retry import Retry

from lightning_hpo.components.servers.db.models import GeneralModel

_CONNECTION_RETRY_TOTAL = 5
_CONNECTION_RETRY_BACKOFF_FACTOR = 0.5


def _configure_session() -> Session:
    """Configures the session for GET and POST requests.

    It enables a generous retrial strategy that waits for the application server to connect.
    """
    retry_strategy = Retry(
        # wait time between retries increases exponentially according to: backoff_factor * (2 ** (retry - 1))
        total=_CONNECTION_RETRY_TOTAL,
        backoff_factor=_CONNECTION_RETRY_BACKOFF_FACTOR,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)
    return http


class DatabaseConnector:
    def __init__(self, model: Type[SQLModel], db_url: str, model_id: Optional[str] = None):
        self.model = model
        self.db_url = db_url
        self.model_id = model_id
        self.session = _configure_session()

    def get(self, config: Optional[Type[SQLModel]] = None):
        cls = config if config else self.model
        resp = self.session.get(self.db_url, data=GeneralModel.from_cls(cls).json())
        assert resp.status_code == 200
        return [cls(**data) for data in resp.json()]

    def post(self, config: SQLModel, model_id: Optional[str] = None):
        resp = self.session.post(
            self.db_url,
            data=GeneralModel.from_obj(config, id=model_id or self.model_id).json(),
        )
        assert resp.status_code == 200

    def put(self, config: SQLModel, model_id: Optional[str] = None):
        resp = self.session.put(
            self.db_url,
            data=GeneralModel.from_obj(config, id=self.model_id or self.model_id).json(),
        )
        assert resp.status_code == 200

    def delete(self, config: SQLModel, model_id: Optional[str] = None):
        resp = self.session.delete(
            self.db_url,
            data=GeneralModel.from_obj(config, id=self.model_id or self.model_id).json(),
        )
        assert resp.status_code == 200
