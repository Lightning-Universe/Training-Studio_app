from typing import List, Optional

from fastapi import FastAPI
from lightning import BuildConfig, LightningWork
from sqlmodel import SQLModel
from uvicorn import run

from lightning_hpo.components.servers.db.models import GeneralModel


class Database(LightningWork):
    def __init__(
        self,
        db_file_name: str = "database.db",
        debug: bool = False,
        models: Optional[List[SQLModel]] = None,  # Just meant to be imported.
    ):
        super().__init__(parallel=True, cloud_build_config=BuildConfig(["sqlmodel"]))
        self.db_file_name = db_file_name
        self.debug = debug
        self._models = models

    def run(self):
        from sqlmodel import create_engine, select, Session, SQLModel

        app = FastAPI()
        engine = create_engine(f"sqlite:///{self.db_file_name}", echo=self.debug)

        @app.on_event("startup")
        def on_startup():
            print(f"Creating the following tables {self._models}")
            SQLModel.metadata.create_all(engine)

        @app.get("/general/")
        async def general_get(config: GeneralModel):
            with Session(engine) as session:
                statement = select(config.data_cls)
                results = session.exec(statement)
                return results.all()

        @app.post("/general/")
        async def general_post(config: GeneralModel):
            with Session(engine) as session:
                data = config.convert_to_model()
                session.add(data)
                session.commit()
                session.refresh(data)
                return data

        @app.put("/general/")
        async def general_put(config: GeneralModel):
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

        run(app, host=self.host, port=self.port)

    def alive(self):
        """Hack: Returns whether the server is alive."""
        return self.url != ""
