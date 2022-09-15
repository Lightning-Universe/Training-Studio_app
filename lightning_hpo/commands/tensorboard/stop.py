from typing import Optional

from sqlmodel import Field, SQLModel

from lightning_hpo.utilities.enum import Stage


class TensorboardConfig(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    sweep_id: str
    shared_folder: str
    stage: str = Stage.NOT_STARTED
    desired_stage: str = Stage.RUNNING
    url: str = ""


class StopTensorboardConfig(SQLModel):
    sweep_id: str
