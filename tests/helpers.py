from typing import Any, Dict
from unittest.mock import MagicMock
from uuid import uuid4

from lightning.app.utilities.enum import make_status, WorkStageStatus

from lightning_hpo import Objective
from lightning_hpo.components.servers.db.connector import DatabaseConnector
from lightning_hpo.components.servers.db.models import GeneralModel
from lightning_hpo.utilities.utils import get_primary_key


class MockResponse:
    def __init__(self, data):
        self.data = data
        self.status_code = 200

    def json(self):
        return self.data


class MockSession:
    def __init__(self, data):
        self.data = data

    def get(self, url, data):
        general = GeneralModel.parse_raw(data)
        return MockResponse(data=[v for name, v in self.data.items() if name.split(":")[0] == general.cls_name])

    def post(self, url, data):
        general = GeneralModel.parse_raw(data)
        data = general.convert_to_model()
        primary_key = get_primary_key(data.__class__)
        if getattr(data, primary_key) is None:
            setattr(data, primary_key, str(uuid4()))
        self.data[self.to_key(data)] = data.dict()
        return MockResponse(data=None)

    def put(self, url, data):
        general = GeneralModel.parse_raw(data)
        data = general.convert_to_model()
        self.data[self.to_key(data)] = data.dict()
        return MockResponse(data=None)

    def delete(self, url, data):
        general = GeneralModel.parse_raw(data)
        data = general.convert_to_model()
        del self.data[self.to_key(data)]
        return MockResponse(data=None)

    @staticmethod
    def to_key(data) -> str:
        return f"{str(data.__class__.__name__)}:{getattr(data, get_primary_key(data.__class__))}"


class MockDatabaseConnector(DatabaseConnector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = {}
        self.session = MockSession(self.data)


class MockObjective(Objective):
    def run(self, params: Dict[str, Any], restart_count: int):
        self.params = params
        self.best_model_path = params.get("best_model_path")
        self.best_model_score = params.get("best_model_score")
        self._backend = MagicMock()
        self.on_after_run()

    def on_after_run(self):
        self._calls["latest_call_hash"] = "test"
        self._calls["test"] = {"statuses": [make_status(WorkStageStatus.SUCCEEDED)]}


class FailedMockObjective(Objective):
    def run(self, params: Dict[str, Any], restart_count: int):
        self.params = params
        self.best_model_path = params["best_model_path"]
        self.best_model_score = params["best_model_score"]
        self._backend = MagicMock()

        self.on_after_run()

    def on_after_run(self):
        self._calls["latest_call_hash"] = "test"
        self._calls["test"] = {"statuses": [make_status(WorkStageStatus.FAILED, message="Error")]}
