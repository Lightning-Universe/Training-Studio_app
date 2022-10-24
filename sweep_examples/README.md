## Installation

Create a new virtual environment with python 3.8+

```bash
python -m venv .venv
source .venv/bin/activate
```

Clone and install lightning-hpo.

```bash
git clone https://github.com/Lightning-AI/lightning-hpo && cd lightning-hpo

pip install -e . -r requirements.txt --find-links https://download.pytorch.org/whl/cpu/torch_stable.html
```

Make sure everything works fine.

```bash
python -m lightning run app app.py
```

______________________________________________________________________

### 1. App Agnostic

This example shows you how to use Lightning HPO with any framework.

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
        total_experiments=50,
        parallel_experiments=10,
        direction="maximize",
        distributions={"x": Uniform(-10, 10)},
    )
)
```

Now, you can optimize it locally.

```bash
python -m lightning run app 1_app_agnostic.py
```

or with ``--cloud`` to run it in the cloud.

```bash
python -m lightning run app 1_app_agnostic.py --cloud
```

> Note: Locally, each experiment runs into its own process, so there is an overhead if your objective is quick to run.

Find the example [here](./1_app_agnostic.py)

______________________________________________________________________

### 2. App PyTorch Lightning

This example shows you how to use Lightning HPO with [PyTorch Lightning](https://pytorch-lightning.readthedocs.io/en/stable/) framework.

Here is how to launch 100 experiments 10 at a times with 2 nodes of 4 GPUs for each in the cloud.

```python
import os.path as ops

from lightning import LightningApp
from lightning_hpo.algorithm import OptunaAlgorithm
from lightning_hpo import Sweep, CloudCompute
from lightning_hpo.distributions import Uniform, IntUniform, Categorical, LogUniform

app = LightningApp(
    Sweep(
        script_path="train.py",
        total_experiments=100,
        parallel_experiments=10,
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
python -m lightning run app 2_app_pytorch_lightning.py --cloud --env WANDB_ENTITY={WANDB_ENTITY} --env WANDB_API_KEY={WANDB_API_KEY}
```

Find the example [here](./2_app_pytorch_lightning.py)

![Lightning App UI](https://pl-flash-data.s3.amazonaws.com/assets_lightning/wandb2.png)

______________________________________________________________________

## Train a 1B+ Large Language Modeling Model with Multi Node Training

Run the App in the cloud

```bash
lightning run app app.py --cloud
```

Connect to the App once ready.

```
lightning connect {APP_NAME} -y
```

Below is an example of how you can train a 1.6B parameter GPT2 transformer model using Lightning Transformers and DeepSpeed using the [Lightning Transformers](https://github.com/Lightning-AI/lightning-transformers) library.

```python
import pytorch_lightning as pl
from lightning_transformers.task.nlp.language_modeling import LanguageModelingDataModule, LanguageModelingTransformer
from transformers import AutoTokenizer

model_name = "gpt2-xl"

tokenizer = AutoTokenizer.from_pretrained(model_name)

model = LanguageModelingTransformer(
    pretrained_model_name_or_path=model_name,
    tokenizer=tokenizer,
    deepspeed_sharding=True,  # defer initialization of the model to shard/load pre-train weights
)

dm = LanguageModelingDataModule(
    batch_size=1,
    dataset_name="wikitext",
    dataset_config_name="wikitext-2-raw-v1",
    tokenizer=tokenizer,
)
trainer = pl.Trainer(
    accelerator="gpu",
    devices="auto",
    strategy="deepspeed_stage_3",
    precision=16,
    max_epochs=1,
)

trainer.fit(model, dm)
```

Run the following command to run a multi node training (2 nodes of 4 V100 GPUS each).

```bash
lightning run experiment big_model.py --requirements deepspeed lightning-transformers==0.2.3 --num_nodes=2 --cloud_compute=gpu-fast-multi --disk_size=80
```


______________________________________________________________________

### 3. App Sklearn

This example shows you how to use Lightning HPO with sklearn and advanced pruning example.

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
        total_experiments=20,
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
python -m lightning run app 3_app_sklearn.py
```

As you can see, several experimentss were pruned (stopped) before they finished all of the iterations. Same as when using pure optuna.

```py
A new study created in memory with name: no-name-a93d848e-a225-4df3-a9c3-5f86680e295d
Experiment 0 finished with value: 0.23684210526315785 and parameters: {'alpha': 0.006779437004523296}. Best is experiment 0 with value: 0.23684210526315785.
Experiment 1 finished with value: 0.07894736842105265 and parameters: {'alpha': 0.008936151407006062}. Best is experiment 1 with value: 0.07894736842105265.
Experiment 2 finished with value: 0.052631578947368474 and parameters: {'alpha': 0.0035836511240528008}. Best is experiment 2 with value: 0.052631578947368474.
Experiment 3 finished with value: 0.052631578947368474 and parameters: {'alpha': 0.0005393218926409795}. Best is experiment 2 with value: 0.052631578947368474.
Experiment 4 finished with value: 0.1578947368421053 and parameters: {'alpha': 6.572557493358585e-05}. Best is experiment 2 with value: 0.052631578947368474.
Experiment 5 finished with value: 0.02631578947368418 and parameters: {'alpha': 0.0013953760106345603}. Best is experiment 5 with value: 0.02631578947368418.
Trail 6 pruned.
Trail 7 pruned.
Trail 8 pruned.
Trail 9 pruned.
Experiment 10 finished with value: 0.07894736842105265 and parameters: {'alpha': 0.00555435554783454}. Best is experiment 5 with value: 0.02631578947368418.
Trail 11 pruned.
Experiment 12 finished with value: 0.052631578947368474 and parameters: {'alpha': 0.025624276147153992}. Best is experiment 5 with value: 0.02631578947368418.
Experiment 13 finished with value: 0.07894736842105265 and parameters: {'alpha': 0.014613957457075546}. Best is experiment 5 with value: 0.02631578947368418.
Trail 14 pruned.
Trail 15 pruned.
Trail 16 pruned.
Experiment 17 finished with value: 0.052631578947368474 and parameters: {'alpha': 0.01028208215647372}. Best is experiment 5 with value: 0.02631578947368418.
Trail 18 pruned.
Trail 19 pruned.
```

Find the example [here](./3_app_sklearn.py)

## Select your logger

Lightning HPO supports Wandb and Streamlit by default.

```python
import optuna

Sweep(..., logger="wandb")
```

```bash
python -m lightning run app app.py --env WANDB_ENTITY=YOUR_USERNAME --env WANDB_API_KEY=YOUR_API_KEY --cloud
```

______________________________________________________________________

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
