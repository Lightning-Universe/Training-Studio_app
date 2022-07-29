from typing import Optional

from sqlmodel import create_engine, Field, SQLModel


class Trial(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sweep_id: str = Field(index=True)
    best_model_score: Optional[float]
    monitor: Optional[str]
    best_model_path: Optional[str]
    name: str


def create_db():
    sqlite_file_name = "database.db"
    sqlite_url = f"sqlite:///{sqlite_file_name}"
    engine = create_engine(sqlite_url, echo=True)
    SQLModel.metadata.create_all(engine)
