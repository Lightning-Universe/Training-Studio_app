from sqlalchemy import Column
from sqlmodel import Field, SQLModel

from lightning_training_studio.distributions import Uniform
from lightning_training_studio.distributions.distributions import Categorical
from lightning_training_studio.utilities.enum import Stage
from lightning_training_studio.utilities.utils import get_best_model_path, get_best_model_score, pydantic_column_type
from tests.helpers import MockObjective


def test_score_and_path():
    from lightning_training_studio.components.sweep import Sweep

    sweep = Sweep(
        5,
        parallel_experiments=3,
        objective_cls=MockObjective,
        distributions={
            "best_model_score": Uniform(0, 100),
            "best_model_path": Categorical(choices=["a", "b", "c", "d", "e", "f", "g"]),
        },
    )
    assert get_best_model_score(sweep) is None
    assert get_best_model_path(sweep) is None

    assert sweep.stage == Stage.NOT_STARTED

    sweep.run()
    assert sweep.stage == Stage.RUNNING
    assert len(sweep.experiments) == 3
    assert sweep.experiments[0]["stage"] == Stage.SUCCEEDED
    assert sweep.w_0.status.stage == Stage.STOPPED

    best_model_score = get_best_model_score(sweep)
    assert best_model_score == max([w.best_model_score for w in sweep.works()])
    best_model_path = [w.best_model_path for w in sweep.works() if w.best_model_score == best_model_score][0]
    assert sweep.best_model_path == best_model_path

    sweep.run()
    assert len(sweep.experiments) == 5
    assert sweep.experiments[4]["stage"] == Stage.SUCCEEDED
    assert sweep.w_4.status.stage == Stage.STOPPED
    assert sweep.stage == Stage.RUNNING

    best_model_score = get_best_model_score(sweep)
    assert best_model_score == max([w.best_model_score for w in sweep.works()])
    best_model_path = [w.best_model_path for w in sweep.works() if w.best_model_score == best_model_score][0]
    assert sweep.best_model_path == best_model_path

    sweep.run()
    assert sweep.stage == Stage.SUCCEEDED


def test_pydantic_column_type():
    class NestedModel(SQLModel):
        name: str

    class Model(SQLModel):
        name: str
        nested_model: NestedModel = Field(..., sa_column=Column(pydantic_column_type(NestedModel)))

    model = Model(name="a", nested_model=NestedModel(name="b"))
    str_repr = model.json()
    new_model = Model.parse_raw(str_repr)
    assert isinstance(new_model.nested_model, NestedModel)
