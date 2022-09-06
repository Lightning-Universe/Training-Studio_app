# Lightning HPO & Training Studio App

Lightning HPO provides a pythonic implementation for Scalable Hyperparameter Tuning.

This library relies on [Optuna](https://optuna.readthedocs.io/en/stable/) for providing state-of-the-art sampling hyper-parameters algorithms and efficient trial pruning strategies.

This is built upon the highly scalable and distributed [Lightning App](https://lightning.ai/lightning-docs/get_started/what_app_can_do.html) framework from [lightning.ai](https://lightning.ai/).

The Training Studio App relies on Lightning HPO to provide abilities to run, show, stop, delete Sweeps, Notebooks, Tensorboard, etc.. 

<div align="center">

<p align="center">
  <a href="https://www.lightning.ai/">Lightning Gallery</a> •
  <a href="https://lightning-ai.github.io/lightning-hpo">Docs</a> •
  <a href="https://github.com/Lightning-AI/lightning-hpo/tree/master/examples">Examples</a>
</p>

[![ReadTheDocs](https://readthedocs.org/projects/pytorch-lightning/badge/?version=stable)](https://lightning-ai.github.io/lightning-hpo)
[![Slack](https://img.shields.io/badge/slack-chat-green.svg?logo=slack)](https://www.pytorchlightning.ai/community)
[![license](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/Lightning-AI/lightning/blob/master/LICENSE)

</div>

## Installation

Create a new virtual environment with python 3.8+

```bash
python -m venv .venv
source .venv/bin/activate
```

Clone and install lightning-hpo.

```bash
git clone https://github.com/Lightning-AI/lightning-hpo.git
cd lightning-hpo
pip install -r requirements.txt -r requirements/test.txt --find-links https://download.pytorch.org/whl/cpu/torch_stable.html
pip install -e .
```

Make sure everything works fine.

```bash
pytest tests --capture=no -v
```


## Getting started

Imagine you want to optimize a simple function called `objective` inside a `objective.py` file.

```python
def objective(x: float):
    return (x - 2) ** 2
```

Import a `Sweep` component, provide the path to your script and what you want to optimize on.

```python
import os.path as ops
from lightning import LightningApp
from lightning_hpo import Sweep
from lightning_hpo.distributions import Uniform

app = LightningApp(
    Sweep(
        script_path="objective.py",
        n_trials=50,
        simultaneous_trials=10,
        direction="maximize",
        distributions={"x": Uniform(-10, 10)},
    )
)
```

Now, you can optimize it locally.

```bash
python -m lightning run app examples/1_app_agnostic.py
```

or with ``--cloud`` to run it in the cloud.

```bash
python -m lightning run app examples/1_app_agnostic.py --cloud
```

> Note: Locally, each trial runs into its own process, so there is an overhead if your objective is quick to run.

Find the example [here](./examples/1_app_agnostic.py)

## PyTorch Lightning Users

Here is how to launch 100 trials 10 at a times with 2 nodes of 4 GPUs for each in the cloud.

```python
import os.path as ops

from lightning import LightningApp
from lightning_hpo.algorithm import OptunaAlgorithm
from lightning_hpo import Sweep, CloudCompute
from lightning_hpo.distributions import Uniform, IntUniform, Categorical, LogUniform

app = LightningApp(
    Sweep(
        script_path="train.py",
        n_trials=100,
        simultaneous_trials=10,
        distributions={
            "model.lr": LogUniform(0.001, 0.1),
            "model.gamma": Uniform(0.5, 0.8),
            "data.batch_size": Categorical([16, 32, 64]),
            "trainer.max_epochs": IntUniform(3, 15),
        },
        algorithm=OptunaAlgorithm(direction="maximize"),
        cloud_compute=CloudCompute("gpu-fast-multi", count=2),  # 2 * 4 V100
        framework="pytorch_lightning",
        logger="wandb",
        sweep_id="Optimizing a Simple CNN over MNIST with Lightning HPO",
    )
)
```

```bash
python -m lightning run app examples/2_app_pytorch_lightning.py --cloud --env WANDB_ENTITY={WANDB_ENTITY} --env WANDB_API_KEY={WANDB_API_KEY}
```

Find the example [here](./examples/2_app_pytorch_lightning.py)

![Lightning App UI](https://pl-flash-data.s3.amazonaws.com/assets_lightning/wandb2.png)

## Convert from raw Optuna to a Lightning App

Below, we are going to convert [Optuna Efficient Optimization Algorithms](https://optuna.readthedocs.io/en/stable/tutorial/10_key_features/003_efficient_optimization_algorithms.html#sphx-glr-tutorial-10-key-features-003-efficient-optimization-algorithms-py>) into a Lightning App.

The Optuna example optimize the value (e.g learning-rate) of a ``SGDClassifier`` from ``sklearn`` trained over the [Iris Dataset](https://archive.ics.uci.edu/ml/datasets/iris).

The example above has been re-organized below in order to run as Lightning App.

```py
from lightning import LightningApp
from sklearn import datasets
import optuna
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split
from lightning_hpo.distributions import LogUniform
from lightning_hpo.algorithm import OptunaAlgorithm
from lightning_hpo import Objective, Sweep


class MyObjective(Objective):

    def objective(self, alpha: float):

        iris = datasets.load_iris()
        classes = list(set(iris.target))
        train_x, valid_x, train_y, valid_y = train_test_split(iris.data, iris.target, test_size=0.25, random_state=0)

        clf = SGDClassifier(alpha=alpha)

        self.monitor = "accuracy"

        for step in range(100):
            clf.partial_fit(train_x, train_y, classes=classes)
            intermediate_value = clf.score(valid_x, valid_y)

            # WARNING: Assign to reports,
            # so the state is instantly sent to the flow.
            self.reports = self.reports + [[intermediate_value, step]]

        self.best_model_score = clf.score(valid_x, valid_y)


app = LightningApp(
    Sweep(
        objective_cls=MyObjective,
        n_trials=20,
        algorithm=OptunaAlgorithm(
            optuna.create_study(pruner=optuna.pruners.MedianPruner()),
            direction="maximize",
        ),
        distributions={"alpha": LogUniform(1e-5, 1e-1)}
    )
)
```

![Lightning App UI](https://pl-flash-data.s3.amazonaws.com/assets_lightning/lightning_hpo_optimizer.png)

```bash
python -m lightning run app examples/3_app_sklearn.py
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

Find the example [here](./examples/3_app_sklearn.py)

## Select your logger

Lightning HPO supports Wandb and Streamlit by default.

```python
import optuna

Sweep(..., logger="wandb")
```

```bash
python -m lightning run app app.py --env WANDB_ENTITY=YOUR_USERNAME --env WANDB_API_KEY=YOUR_API_KEY --cloud
```

## Use advanced algorithms with your Lightning App

Here is how to use the latest research such as [Hyperband paper](http://www.jmlr.org/papers/volume18/16-558/16-558.pdf)

```python
from lightning_hpo.algorithm import OptunaAlgorithm
import optuna

Sweep(
    algorithm=OptunaAlgorithm(
        optuna.create_study(
            direction="maximize",
            pruner=optuna.pruners.HyperbandPruner(
                min_resource=1,
                max_resource=3,
                reduction_factor=3,
            ),
        )
    )
)
```

Learn more [here](https://optuna.readthedocs.io/en/stable/tutorial/10_key_features/003_efficient_optimization_algorithms.html?highlight=hyperband#activating-pruners)


## The Training App (WIP)

In terminal 1, run the Training Application.

```bash
python -m lightning run app examples/4_app_sweeper.py --env WANDB_ENTITY={ENTITY} --env WANDB_API_KEY={API_KEY}
```

In terminal 2, connect to the App and run your first sweep or start your notebook.

```bash
lightning connect localhost
```

```bash
lightning --help

You are connected to the local Lightning App.
Usage: lightning [OPTIONS] COMMAND [ARGS]...

  --help     Show this message and exit.

Lightning App Commands
  delete sweep
  download artefacts
  run notebook
  run sweep
  show artefacts
  show sweeps
  stop sweep
```

```bash
cd examples/scripts && lightning run sweep train.py --n_trials=3 --model.lr="log_uniform(0.001, 0.1)" --logger="wandb" --direction=maximize
```
