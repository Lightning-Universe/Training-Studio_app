import inspect
import sys
from typing import Optional

from pydantic import BaseModel
from sqlmodel import Field, SQLModel


class GeneralModel(BaseModel):
    cls_name: str
    cls_module: str
    data: str
    id: Optional[str]

    def convert_to_model(self):
        return self.data_cls.parse_raw(self.data)

    @property
    def data_cls(self) -> BaseModel:
        return getattr(sys.modules[self.cls_module], self.cls_name)

    @classmethod
    def from_obj(cls, obj, id: Optional[str] = None):
        return cls(
            **{
                "cls_path": inspect.getfile(obj.__class__),
                "cls_name": obj.__class__.__name__,
                "cls_module": obj.__class__.__module__,
                "data": obj.json(),
                "id": id,
            }
        )

    @classmethod
    def from_cls(cls, obj_cls, id: Optional[str] = None):
        return cls(
            **{
                "cls_path": inspect.getfile(obj_cls),
                "cls_name": obj_cls.__name__,
                "cls_module": obj_cls.__module__,
                "data": "",
                "id": id,
            }
        )


class Trial(SQLModel, table=False):
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
