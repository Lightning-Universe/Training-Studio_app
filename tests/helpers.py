from uuid import uuid4

from lightning_hpo.components.servers.db.connector import DatabaseConnector
from lightning_hpo.components.servers.db.models import GeneralModel


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
        return MockResponse(data=[v for _, v in self.data.items()])

    def post(self, url, data):
        general = GeneralModel.parse_raw(data)
        data = general.convert_to_model()
        if getattr(data, general.id) is None:
            setattr(data, general.id, str(uuid4()))
        self.data[getattr(data, general.id)] = data.dict()
        return MockResponse(data=None)

    def put(self, url, data):
        general = GeneralModel.parse_raw(data)
        data = general.convert_to_model()
        self.data[getattr(data, general.id)] = data.dict()
        return MockResponse(data=None)


class MockDatabaseConnector(DatabaseConnector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = {}
        self.session = MockSession(self.data)
