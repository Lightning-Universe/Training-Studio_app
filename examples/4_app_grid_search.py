import os.path as ops

from lightning import LightningApp

from lightning_hpo import Sweep
from lightning_hpo.algorithm import GridSearch

app = LightningApp(
    Sweep(
        script_path=ops.join(ops.dirname(__file__), "scripts/objective.py"),
        n_trials=3,
        simultaneous_trials=1,
        algorithm=GridSearch(search_space={"x": [-10, 0, 10]}),
    )
)
