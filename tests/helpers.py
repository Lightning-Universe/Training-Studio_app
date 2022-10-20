from typing import Any, Callable, Dict, Optional, Type
from unittest.mock import MagicMock
from uuid import uuid4

from lightning.app.components.database.client import DatabaseClient
from lightning.app.components.database.utilities import _GeneralModel
from lightning.app.utilities.commands import ClientCommand
from lightning.app.utilities.enum import make_status, WorkStageStatus

from lightning_hpo import Objective
from lightning_hpo.utilities.utils import get_primary_key


class MockResponse:
    def __init__(self, data):
        self.data = data
        self.status_code = 200

    def json(self):
        return self.data


class MockSession:
    def __init__(self, model, data):
        self.model = model
        self.data = data

    def post(self, url, data):
        if "select_all" in url:
            return self.select_all(url, data)
        elif "insert" in url:
            return self.insert(url, data)
        elif "update" in url:
            return self.update(url, data)
        else:
            return self.delete(url, data)

    def select_all(self, url, data):
        general = _GeneralModel.parse_raw(data)
        return MockResponse(data=[v for name, v in self.data.items() if name.split(":")[0] == general.cls_name])

    def insert(self, url, data):
        primary_key = get_primary_key(self.model)
        general = _GeneralModel.parse_raw(data)
        data = self.model.parse_raw(general.data)
        if getattr(data, primary_key) is None:
            setattr(data, primary_key, str(uuid4()))
        self.data[self.to_key(data)] = data.dict()
        return MockResponse(data=None)

    def update(self, url, data):
        general = _GeneralModel.parse_raw(data)
        data = self.model.parse_raw(general.data)
        self.data[self.to_key(data)] = data.dict()
        return MockResponse(data=None)

    def delete(self, url, data):
        general = _GeneralModel.parse_raw(data)
        data = self.model.parse_raw(general.data)
        del self.data[self.to_key(data)]
        return MockResponse(data=None)

    @staticmethod
    def to_key(data) -> str:
        return f"{str(data.__class__.__name__)}:{getattr(data, get_primary_key(data.__class__))}"


class MockDatabaseClient(DatabaseClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = {}
        self._session = MockSession(self.model, self.data)


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


def _create_client_command_mock(
    cls: Type[ClientCommand], method: Optional[Callable], state: Dict, config_verification: Callable
):
    class MockClientCommand(cls):
        def __init__(self, method, state, payload):
            super().__init__(method)
            self._state = state
            self.config_verification = config_verification

        @property
        def state(self):
            return self._state

        def invoke_handler(self, config):
            self.config_verification(config)

    return MockClientCommand(method, state, config_verification)
