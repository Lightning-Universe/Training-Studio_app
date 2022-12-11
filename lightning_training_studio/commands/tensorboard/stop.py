from sqlmodel import Field, SQLModel

from lightning_training_studio.utilities.enum import Stage


class TensorboardConfig(SQLModel, table=True):
    sweep_id: str = Field(primary_key=True)
    shared_folder: str
    stage: str = Stage.NOT_STARTED
    desired_stage: str = Stage.RUNNING
    url: str = ""


class StopTensorboardConfig(SQLModel):
    sweep_id: str
