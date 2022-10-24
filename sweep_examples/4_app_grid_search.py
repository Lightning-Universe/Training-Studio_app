import os.path as ops

from lightning import LightningApp

from lightning_hpo import Sweep
from lightning_hpo.algorithm import GridSearch

app = LightningApp(
    Sweep(
        script_path=ops.join(ops.dirname(__file__), "scripts/objective.py"),
        total_experiments=3,
        parallel_experiments=1,
        algorithm=GridSearch(search_space={"x": [-10, 0, 10]}),
    )
)
