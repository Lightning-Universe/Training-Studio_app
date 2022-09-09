from uuid import uuid4

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

    def get(self, *args, **kwargs):
        return MockResponse(data=[v for _, v in self.data.items()])

    def post(self, url, data):
        general = GeneralModel.parse_raw(data)
        data = general.convert_to_model()
        primary_key = get_primary_key(data.__class__)
        if getattr(data, primary_key) is None:
            setattr(data, primary_key, str(uuid4()))
        self.data[getattr(data, primary_key)] = data.dict()
        return MockResponse(data=None)

    def put(self, url, data):
        general = GeneralModel.parse_raw(data)
        data = general.convert_to_model()
        primary_key = get_primary_key(data.__class__)
        self.data[getattr(data, primary_key)] = data.dict()
        return MockResponse(data=None)

    def delete(self, url, data):
        general = GeneralModel.parse_raw(data)
        data = general.convert_to_model()
        primary_key = get_primary_key(data.__class__)
        del self.data[getattr(data, primary_key)]
        return MockResponse(data=None)


class MockDatabaseConnector(DatabaseConnector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = {}
        self.session = MockSession(self.data)
