from typing import Optional

from sqlmodel import Field, SQLModel

from lightning_hpo.utilities.enum import Status


class TensorboardConfig(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sweep_id: str
    shared_folder: str
    status: str = Status.NOT_STARTED
    desired_state: str = Status.RUNNING
