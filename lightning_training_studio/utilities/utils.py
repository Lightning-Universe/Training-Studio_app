import functools
import json
from dataclasses import dataclass
from typing import Generic, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from lightning import CloudCompute as LightningCloudCompute
from lightning import LightningFlow
from lightning.app.storage import Path
from lightning.app.utilities.enum import WorkStageStatus
from pydantic import parse_obj_as
from pydantic.main import ModelMetaclass
from sqlalchemy.inspection import inspect
from sqlmodel import JSON, SQLModel, TypeDecorator

from lightning_training_studio.framework import _OBJECTIVE_FRAMEWORK
from lightning_training_studio.framework.agnostic import Objective

T = TypeVar("T")


@dataclass
class HPOCloudCompute(LightningCloudCompute):
    count: int = 1


def get_best_model_score(flow: LightningFlow) -> Optional[float]:
    metrics = [work.best_model_score for work in flow.works()]
    if not metrics or not all(metrics):
        return None
    return max(metrics)


def get_best_model_path(flow: LightningFlow) -> Optional[Path]:
    metrics = {work.best_model_score: work for work in flow.works()}
    if not all(metrics) or all(metric is None for metric in metrics):
        return None

    return metrics[max(metrics)].best_model_path


def _resolve_objective_cls(objective_cls, framework: str):
    if objective_cls is None:
        if framework not in _OBJECTIVE_FRAMEWORK:
            raise Exception(f"The supported framework are {list(_OBJECTIVE_FRAMEWORK)}. Found {framework}.")
        objective_cls = _OBJECTIVE_FRAMEWORK[framework]

    return objective_cls


def _check_stage(obj: Union[LightningFlow, Objective], status: str) -> bool:
    if isinstance(obj, Objective):
        return obj.status.stage == status
    else:
        works = obj.works()
        if works:
            return any(w.status.stage == status for w in obj.works())
        else:
            return status == WorkStageStatus.NOT_STARTED


# Taken from https://github.com/tiangolo/sqlmodel/issues/63#issuecomment-1081555082
def pydantic_column_type(pydantic_type):
    class PydanticJSONType(TypeDecorator, Generic[T]):
        impl = JSON()

        def __init__(
            self,
            json_encoder=json,
        ):
            self.json_encoder = json_encoder
            super(PydanticJSONType, self).__init__()

        def bind_processor(self, dialect):
            impl_processor = self.impl.bind_processor(dialect)
            dumps = self.json_encoder.dumps
            if impl_processor:

                def process(value: T):
                    if value is not None:
                        if isinstance(pydantic_type, ModelMetaclass):
                            # This allows to assign non-InDB models and if they're
                            # compatible, they're directly parsed into the InDB
                            # representation, thus hiding the implementation in the
                            # background. However, the InDB model will still be returned
                            value_to_dump = pydantic_type.from_orm(value)
                        else:
                            value_to_dump = value
                        value = jsonable_encoder(value_to_dump)
                    return impl_processor(value)

            else:

                def process(value):
                    if isinstance(pydantic_type, ModelMetaclass):
                        # This allows to assign non-InDB models and if they're
                        # compatible, they're directly parsed into the InDB
                        # representation, thus hiding the implementation in the
                        # background. However, the InDB model will still be returned
                        value_to_dump = pydantic_type.from_orm(value)
                    else:
                        value_to_dump = value
                    value = dumps(jsonable_encoder(value_to_dump))
                    return value

            return process

        def result_processor(self, dialect, coltype) -> T:
            impl_processor = self.impl.result_processor(dialect, coltype)
            if impl_processor:

                def process(value):
                    value = impl_processor(value)
                    if value is None:
                        return None

                    data = value
                    # Explicitly use the generic directly, not type(T)
                    full_obj = parse_obj_as(pydantic_type, data)
                    return full_obj

            else:

                def process(value):
                    if value is None:
                        return None

                    # Explicitly use the generic directly, not type(T)
                    full_obj = parse_obj_as(pydantic_type, value)
                    return full_obj

            return process

        def compare_values(self, x, y):
            return x == y

    return PydanticJSONType


@functools.lru_cache
def get_primary_key(model_type: Type[SQLModel]) -> str:
    primary_keys = inspect(model_type).primary_key

    if len(primary_keys) != 1:
        raise ValueError(f"The model {model_type.__name__} should have a single primary key field.")

    return primary_keys[0].name
