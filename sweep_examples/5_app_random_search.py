import os.path as ops

from lightning import LightningApp

from lightning_training_studio import Sweep
from lightning_training_studio.algorithm import RandomSearch
from lightning_training_studio.distributions import Uniform

app = LightningApp(
    Sweep(
        script_path=ops.join(ops.dirname(__file__), "scripts/objective.py"),
        total_experiments=3,
        parallel_experiments=1,
        algorithm=RandomSearch(distributions={"x": Uniform(-10, 10)}),
    )
)
