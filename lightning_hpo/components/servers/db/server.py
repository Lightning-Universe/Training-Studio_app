from fastapi import FastAPI
from lightning import BuildConfig, LightningWork
from uvicorn import run

from lightning_hpo.components.servers.db.models import Trial


class Database(LightningWork):
    def __init__(
        self,
        db_file_name: str = "database.db",
    ):
        super().__init__(parallel=True, cloud_build_config=BuildConfig(["sqlmodel"]))
        self.db_file_name = db_file_name

    def run(self):
        from sqlmodel import create_engine, Session, SQLModel

        app = FastAPI()
        engine = create_engine(f"sqlite:///{self.db_file_name}", echo=True)

        @app.on_event("startup")
        def on_startup():
            SQLModel.metadata.create_all(engine)

        @app.post("/trial/")
        def insert_trial(trial: Trial):
            with Session(engine) as session:
                session.add(trial)
                session.commit()
                session.refresh(trial)
                return trial

        run(app, host=self.host, port=self.port)

    def alive(self):
        """Hack: Returns whether the server is alive."""
        return self.url != ""
