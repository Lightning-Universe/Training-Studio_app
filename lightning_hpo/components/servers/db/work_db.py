import asyncio
import os
import pathlib
import sys
from typing import List, Optional, Type

import uvicorn
from fastapi import FastAPI
from lightning import BuildConfig, LightningWork
from lightning_app.storage import Drive
from lightning_app.utilities.app_helpers import Logger
from sqlmodel import select, Session, SQLModel

from lightning_hpo.components.servers.db.models import GeneralModel
from lightning_hpo.utilities.utils import get_primary_key

logger = Logger(__name__)

engine = None


def general_get(config: GeneralModel):
    with Session(engine) as session:
        statement = select(config.data_cls)
        results = session.exec(statement)
        return results.all()


def general_post(config: GeneralModel):
    with Session(engine) as session:
        data = config.convert_to_model()
        session.add(data)
        session.commit()
        session.refresh(data)
        return data


def general_put(config: GeneralModel):
    with Session(engine) as session:
        update_data = config.convert_to_model()
        primary_key = get_primary_key(update_data.__class__)
        identifier = getattr(update_data.__class__, primary_key, None)
        statement = select(update_data.__class__).where(identifier == getattr(update_data, primary_key))
        results = session.exec(statement)
        result = results.one()
        for k, v in vars(update_data).items():
            if k in ("id", "_sa_instance_state"):
                continue
            if getattr(result, k) != v:
                setattr(result, k, v)
        session.add(result)
        session.commit()
        session.refresh(result)


def general_delete(config: GeneralModel):
    with Session(engine) as session:
        update_data = config.convert_to_model()
        primary_key = get_primary_key(update_data.__class__)
        identifier = getattr(update_data.__class__, primary_key, None)
        statement = select(update_data.__class__).where(identifier == getattr(update_data, primary_key))
        results = session.exec(statement)
        result = results.one()
        session.delete(result)
        session.commit()


def create_engine(db_file_name: str, models: List[Type[SQLModel]], echo: bool):
    global engine

    from sqlmodel import create_engine, SQLModel

    engine = create_engine(f"sqlite:///{pathlib.Path(db_file_name).resolve()}", echo=echo)

    logger.debug(f"Creating the following tables {models}")
    try:
        SQLModel.metadata.create_all(engine)
    except Exception as e:
        logger.debug(e)


class DatabaseUvicornServer(uvicorn.Server):

    has_started_queue = None

    def run(self, sockets=None):
        self.config.setup_event_loop()
        loop = asyncio.get_event_loop()
        asyncio.ensure_future(self.serve(sockets=sockets))
        loop.run_forever()

    def install_signal_handlers(self):
        """Ignore Uvicorn Signal Handlers"""


class Database(LightningWork):
    def __init__(
        self,
        db_file_name: str = "database.db",
        debug: bool = False,
        models: Optional[List[Type[SQLModel]]] = None,  # Just meant to be imported.
    ):
        super().__init__(parallel=True, cloud_build_config=BuildConfig(["sqlmodel"]))
        self.db_file_name = db_file_name
        self.debug = debug
        self._models = models
        self.drive = Drive("lit://database")

    def run(self):
        if self.drive.list():
            self.drive.get(self.db_file_name)
            print("Retrieved the database from Drive.")

        app = FastAPI()

        create_engine(self.db_file_name, self._models, self.debug)
        app.get("/general/")(general_get)
        app.post("/general/")(general_post)
        app.put("/general/")(general_put)
        app.delete("/general/")(general_delete)

        print(f"Database is ready PID: {os.getpid()}")

        sys.modules["uvicorn.main"].Server = DatabaseUvicornServer

        uvicorn.run(app, host=self.host, port=self.port, log_level="error")

    def alive(self):
        """Hack: Returns whether the server is alive."""
        return self.db_url != ""

    @property
    def db_url(self) -> Optional[str]:
        use_localhost = "LIGHTNING_APP_STATE_URL" not in os.environ
        if use_localhost:
            return self.url
        if self.internal_ip != "":
            return f"http://{self.internal_ip}:{self.port}"
        return self.internal_ip

    def on_exit(self):
        self.drive.put(self.db_file_name)
        print("Stored the database to the Drive.")
