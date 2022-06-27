# Lightning HPO

Lightning provides the most pythonic implementation for Scalable Hyperparameter Tuning.

This library relies on [Optuna](https://optuna.readthedocs.io/en/stable/) for providing state-of-the-art sampling hyper-parameters algorithms and efficient trial pruning strategies.

### Installation

```bash
git clone https://github.com/PyTorchLightning/lightning-hpo.git
pip install -e .
```

### How to use

The only provided classes are: `BaseObjective` and `Optimizer`.

```py
import optuna
from lightning_hpo import BaseObjective, Optimizer

class MyCustomObjective(BaseObjective):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.best_model_path = None

    def on_after_run(self, result):
        self.best_model_score = float(result["best_model_score"])

    @staticmethod
    def distributions():
        return {"learning_rate": optuna.distributions.LogUniformDistribution(0.0001, 0.1)}


component = Optimizer(
    script_path=`{RELATIVE_PATH_TO_YOUR_SCRIPT}`,
    total_trials=100,
    simultaneous_trials=5,
    objective_work_cls=MyCustomObjective,
)
```

### Example

```bash
python -m lightning run app app.py
```

### Convert from Optuna.

Below, we are going to convert [Optuna Efficient Optimization Algorithms](https://optuna.readthedocs.io/en/stable/tutorial/10_key_features/003_efficient_optimization_algorithms.html#sphx-glr-tutorial-10-key-features-003-efficient-optimization-algorithms-py>) into a Lightning App.

The Optuna example optimize the value (e.g learning-rate) of a ``SGDClassifier`` from ``sklearn`` trained over the [Iris Dataset](https://archive.ics.uci.edu/ml/datasets/iris).

```py
import optuna
from lightning_hpo import BaseObjective, Optimizer
from optuna.distributions import LogUniformDistribution
from sklearn import datasets
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split

from lightning import LightningApp, LightningFlow


class Objective(BaseObjective):
    def run(self, trial_id, params):
        # WARNING: Don't forget to assign those to self,
        # so they get tracked in the state.
        self.trial_id = trial_id
        self.params = params

        iris = datasets.load_iris()
        classes = list(set(iris.target))
        train_x, valid_x, train_y, valid_y = train_test_split(
            iris.data, iris.target, test_size=0.25, random_state=0)

        clf = SGDClassifier(alpha=params["alpha"])

        for step in range(100):
            clf.partial_fit(train_x, train_y, classes=classes)
            intermediate_value = 1.0 - clf.score(valid_x, valid_y)

            # WARNING: Assign to reports,
            # so the state is instantly sent to the flow.
            self.reports = self.reports + [[intermediate_value, step]]

        self.best_model_score = 1.0 - clf.score(valid_x, valid_y)

    def distributions(self):
        return {"alpha": LogUniformDistribution(1e-5, 1e-1)}


class RootFlow(LightningFlow):
    def __init__(self):
        super().__init__()
        self.optimizer = Optimizer(
            objective_work_cls=Objective,
            total_trials=20,
            study=optuna.create_study(pruner=optuna.pruners.MedianPruner()),
        )

    def run(self):
        self.optimizer.run()

    def configure_layout(self):
        return {"name": "HyperPlot", "content": self.optimizer.hi_plot}


app = LightningApp(RootFlow())
```


### Customize your HPO training with Optuna advanced algorithms

Here is how to use the latest research such as [Hyperband paper](http://www.jmlr.org/papers/volume18/16-558/16-558.pdf)

```python
import optuna

Optimizer(
    study=optuna.create_study(
        direction="maximize",
        pruner=optuna.pruners.HyperbandPruner(
            min_resource=1, max_resource=n_train_iter, reduction_factor=3
    ),
)
```

```bash
python -m lightning run app app_hyperband.py --cloud
```

Learn more [here](https://optuna.readthedocs.io/en/stable/tutorial/10_key_features/003_efficient_optimization_algorithms.html?highlight=hyperband#activating-pruners)
