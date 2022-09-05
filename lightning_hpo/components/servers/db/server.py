import os
from typing import List, Optional, Type

from fastapi import FastAPI
from lightning import BuildConfig, LightningWork
from lightning.app.storage import Path
from sqlmodel import create_engine, select, Session, SQLModel
from uvicorn import run

from lightning_hpo.components.servers.db.models import GeneralModel

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
        assert config.id
        update_data = config.convert_to_model()
        identifier = getattr(update_data.__class__, config.id, None)
        statement = select(update_data.__class__).where(identifier == getattr(update_data, config.id))
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
        assert config.id
        update_data = config.convert_to_model()
        identifier = getattr(update_data.__class__, config.id, None)
        statement = select(update_data.__class__).where(identifier == getattr(update_data, config.id))
        results = session.exec(statement)
        result = results.one()
        session.delete(result)
        session.commit()


class Database(LightningWork):
    def __init__(
        self,
        db_file_name: str = "database.db",
        debug: bool = False,
        models: Optional[List[Type[SQLModel]]] = None,  # Just meant to be imported.
    ):
        super().__init__(parallel=True, cloud_build_config=BuildConfig(["sqlmodel"]))
        self.db_file_name = Path(db_file_name)
        self.debug = debug
        self._models = models

    def run(self):
        global engine

        app = FastAPI()
        engine = create_engine(f"sqlite:///{self.db_file_name}", echo=self.debug)

        @app.on_event("startup")
        def on_startup():
            print(f"Creating the following tables {self._models}")
            SQLModel.metadata.create_all(engine)

        app.get("/general/")(general_get)
        app.post("/general/")(general_post)
        app.put("/general/")(general_put)
        app.delete("/general/")(general_delete)

        run(app, host=self.host, port=self.port, log_level="error")

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
