from typing import Optional

from sqlmodel import Field, SQLModel


class Trial(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sweep_id: str = Field(index=True)
    trial_id: int
    best_model_score: Optional[float]
    monitor: Optional[str]
    best_model_path: Optional[str]
    name: str
    has_succeeded: bool
    url: Optional[str]
    params: Optional[str]
