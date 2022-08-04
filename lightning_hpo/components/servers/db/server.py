from typing import List

from fastapi import FastAPI
from lightning import BuildConfig, LightningWork
from uvicorn import run

from lightning_hpo.commands.sweep import SweepConfig

# from lightning_hpo.components.servers.db.models import Trial


class Database(LightningWork):
    def __init__(
        self,
        db_file_name: str = "database.db",
        debug: bool = False,
    ):
        super().__init__(parallel=True, cloud_build_config=BuildConfig(["sqlmodel"]))
        self.db_file_name = db_file_name
        self.debug = debug

    def run(self):
        from sqlmodel import create_engine, select, Session, SQLModel

        app = FastAPI()
        engine = create_engine(f"sqlite:///{self.db_file_name}", echo=self.debug)

        @app.on_event("startup")
        def on_startup():
            SQLModel.metadata.create_all(engine)

        @app.post("/sweep/")
        async def insert_sweep(sweep: SweepConfig):
            with Session(engine) as session:
                session.add(sweep)
                session.commit()
                session.refresh(sweep)
                return sweep

        @app.put("/sweep/")
        async def update_sweep(update: SweepConfig):
            with Session(engine) as session:
                statement = select(SweepConfig).where(SweepConfig.sweep_id == update.sweep_id)
                results = session.exec(statement)
                sweep = results.one()
                for k, v in vars(update).items():
                    if k in ("id", "_sa_instance_state"):
                        continue
                    if getattr(sweep, k) != v:
                        setattr(sweep, k, v)
                session.add(sweep)
                session.commit()

        @app.get("/reconcile_sweeps/")
        async def reconcile_sweeps() -> List[SweepConfig]:
            with Session(engine) as session:
                statement = select(SweepConfig).where(SweepConfig.n_trials > SweepConfig.trials_done)
                results = session.exec(statement)
                sweeps = results.all()
                return sweeps

        @app.get("/sweep")
        async def collect_trials() -> List[SweepConfig]:
            with Session(engine) as session:
                return session.exec(select(SweepConfig)).all()

        run(app, host=self.host, port=self.port)

    def alive(self):
        """Hack: Returns whether the server is alive."""
        return self.url != ""
