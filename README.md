# Lightning HPO

Lightning provides the most pythonic implementation for Scalable Hyperparameter Tuning.

This library relies on [Optuna](https://optuna.readthedocs.io/en/stable/) for providing state-of-the-art sampling hyper-parameters algorithms and efficient trial pruning strategies.

## Installation

```bash
git clone https://github.com/PyTorchLightning/lightning-hpo.git
pip install -e .
```

## Use Lightning HPO in your app.

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
    n_trials=100,
    simultaneous_trials=5,
    objective_cls=MyCustomObjective,
)
```

Run the example with the following command:

```bash
python -m lightning run app app.py
```

## Convert existing from Optuna scripts to a scalable Lightning App

Below, we are going to convert [Optuna Efficient Optimization Algorithms](https://optuna.readthedocs.io/en/stable/tutorial/10_key_features/003_efficient_optimization_algorithms.html#sphx-glr-tutorial-10-key-features-003-efficient-optimization-algorithms-py>) into a Lightning App.

The Optuna example optimize the value (e.g learning-rate) of a ``SGDClassifier`` from ``sklearn`` trained over the [Iris Dataset](https://archive.ics.uci.edu/ml/datasets/iris).

The example above has been re-organized below in order to run as Lightning App.

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
            objective_cls=Objective,
            n_trials=20,
            study=optuna.create_study(pruner=optuna.pruners.MedianPruner()),
        )

    def run(self):
        self.optimizer.run()

    def configure_layout(self):
        return {"name": "HyperPlot", "content": self.optimizer.hi_plot}


app = LightningApp(RootFlow())
```

Now, your code can run at scale in the cloud by adding the flag ``--cloud``. Plus, you get a neat UI to track the optimization.

![Lightning App UI](https://pl-flash-data.s3.amazonaws.com/assets_lightning/lightning_hpo_optimizer.png)

Simply run the following commands:

```py
lightning run app app_sklearn.py
```

As you can see, several trials were pruned (stopped) before they finished all of the iterations. Same as when using pure optuna.

```py
A new study created in memory with name: no-name-a93d848e-a225-4df3-a9c3-5f86680e295d
Trial 0 finished with value: 0.23684210526315785 and parameters: {'alpha': 0.006779437004523296}. Best is trial 0 with value: 0.23684210526315785.
Trial 1 finished with value: 0.07894736842105265 and parameters: {'alpha': 0.008936151407006062}. Best is trial 1 with value: 0.07894736842105265.
Trial 2 finished with value: 0.052631578947368474 and parameters: {'alpha': 0.0035836511240528008}. Best is trial 2 with value: 0.052631578947368474.
Trial 3 finished with value: 0.052631578947368474 and parameters: {'alpha': 0.0005393218926409795}. Best is trial 2 with value: 0.052631578947368474.
Trial 4 finished with value: 0.1578947368421053 and parameters: {'alpha': 6.572557493358585e-05}. Best is trial 2 with value: 0.052631578947368474.
Trial 5 finished with value: 0.02631578947368418 and parameters: {'alpha': 0.0013953760106345603}. Best is trial 5 with value: 0.02631578947368418.
Trail 6 pruned.
Trail 7 pruned.
Trail 8 pruned.
Trail 9 pruned.
Trial 10 finished with value: 0.07894736842105265 and parameters: {'alpha': 0.00555435554783454}. Best is trial 5 with value: 0.02631578947368418.
Trail 11 pruned.
Trial 12 finished with value: 0.052631578947368474 and parameters: {'alpha': 0.025624276147153992}. Best is trial 5 with value: 0.02631578947368418.
Trial 13 finished with value: 0.07894736842105265 and parameters: {'alpha': 0.014613957457075546}. Best is trial 5 with value: 0.02631578947368418.
Trail 14 pruned.
Trail 15 pruned.
Trail 16 pruned.
Trial 17 finished with value: 0.052631578947368474 and parameters: {'alpha': 0.01028208215647372}. Best is trial 5 with value: 0.02631578947368418.
Trail 18 pruned.
Trail 19 pruned.
```

## Use advanced algorithms with your Lightning App

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
