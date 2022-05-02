# Lightning Tune

Lightning provides the most pythonic implementaiton for Scalable Hyperparameter Tuning.

This library relies on [Optuna](https://optuna.readthedocs.io/en/stable/) for the state-of-the-art algorithms for sampling hyperparameters and efficiently pruning unpromising trials.


```py
import optuna
from lightning_hpo import AbstractObjectiveWork, OptunaPythonScript

class MyCustomObjective(AbstractObjectiveWork):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.best_model_path = None

    def on_after_run(self, res):
        self.best_model_score = float(res["cli"].trainer.checkpoint_callback.best_model_score)

    @staticmethod
    def distributions():
        return {"learning_reate": optuna.distributions.LogUniformDistribution(0.0001, 0.1)}


component = OptunaPythonScript(
    script_path=`{PATH_TO_YOUR_SCRIPT}`,
    total_trials=4,
    simultaneous_trials=2,
    objective_work_cls=MyCustomObjective,
    script_args=`{YOUR_DEFAULT_ARGUMENTS}`,
)
```