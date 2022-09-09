from typing import Optional

from sqlmodel import Field, SQLModel

from lightning_hpo.utilities.enum import State


class TensorboardConfig(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sweep_id: str
    shared_folder: str
    state: str = State.NOT_STARTED
    desired_state: str = State.RUNNING
    url: Optional[str] = None
