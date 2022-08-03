from typing import List

from fastapi import FastAPI
from lightning import BuildConfig, LightningWork
from uvicorn import run

from lightning_hpo.commands.sweep import SweepConfig
from lightning_hpo.components.servers.db.models import Trial


class Database(LightningWork):
    def __init__(
        self,
        db_file_name: str = "database.db",
    ):
        super().__init__(parallel=True, cloud_build_config=BuildConfig(["sqlmodel"]))
        self.db_file_name = db_file_name

    def run(self):
        from sqlmodel import create_engine, select, Session, SQLModel

        app = FastAPI()
        engine = create_engine(f"sqlite:///{self.db_file_name}", echo=True)

        @app.on_event("startup")
        def on_startup():
            SQLModel.metadata.create_all(engine)

        @app.post("/trial/")
        async def insert_trial(trial: Trial):
            with Session(engine) as session:
                session.add(trial)
                session.commit()
                session.refresh(trial)
                return trial

        @app.post("/sweep/")
        async def insert_sweep(sweep: SweepConfig):
            with Session(engine) as session:
                print(sweep)
                session.add(sweep)
                session.commit()
                session.refresh(sweep)
                return sweep

        @app.put("/sweep/")
        async def update_sweep(sweep_id: str, num_trials: int):
            with Session(engine) as session:
                statement = select(SweepConfig).where(SweepConfig.sweep_id == sweep_id)
                results = session.exec(statement)
                sweeps = results.all()
                assert len(sweeps) == 1
                sweep = sweeps[0]
                sweep.num_trials = int(num_trials)
                session.add(sweep)
                session.commit()
                session.refresh(sweep)

        @app.get("/trials/")
        async def collect_trials() -> List[Trial]:
            with Session(engine) as session:
                return session.exec(select(Trial)).all()

        run(app, host=self.host, port=self.port)

    def alive(self):
        """Hack: Returns whether the server is alive."""
        return self.url != ""
