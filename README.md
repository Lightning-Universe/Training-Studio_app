<div align="center">
    <h1>
        Research Studio App
    </h1>
    <img src="https://pl-flash-data.s3.amazonaws.com/assets_lightning/lightning_hpo_logo.png">

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

The [Research Studio App](https://lightning-ai.github.io/lightning-hpo/training_studio.html) is a full-stack AI application built using the [Lightning App](https://lightning.ai/lightning-docs/) framework to enable running experiments or sweeps with state-of-the-art sampling hyper-parameters algorithms and efficient experiment pruning strategies and more.

Learn more [here](https://github.com/Lightning-AI/lightning-hpo#the-training-studio-app).

</div>

______________________________________________________________________

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

Check the [documentation](https://lightning-ai.github.io/lightning-hpo) to learn more !

______________________________________________________________________

## Run the Research Studio App locally

In your first terminal, run the Lightning App.

```bash
python -m lightning run app app.py.
```

In second terminal, connect to the Lightning App and download its CLI.

```bash
python -m lightning connect localhost -y
```

```bash
python -m lightning --help

Usage: lightning [OPTIONS] COMMAND [ARGS]...

  --help     Show this message and exit.

Lightning App Commands
  create drive       Create a Drive.
  delete drive       Delete a Drive.
  delete experiment  Delete an Experiment.
  delete sweep       Delete a Sweep.
  download artifacts Download an artifact.
  run experiment     Run an Experiment.
  run sweep          Run a Sweep.
  show artifacts     Show artifacts.
  show drives        Show Drives.
  show experiments   Show Experiments.
  show sweeps        Show all Sweeps or the Experiments from a given Sweep.
  stop experiment    Stop an Experiment.
  stop sweep         Stop a Sweep.

You are connected to the local Lightning App. Return to the primary CLI with `lightning disconnect`.
```

Run your first Sweep from [sweep_examples/scripts](./sweep_examples/scripts) folder

```bash
lightning run sweep train.py --model.lr "[0.001, 0.01, 0.1]" --data.batch "[32, 64]" --algorithm="grid_search" --requirements 'jsonargparse[signatures]>=4.15.2'
```

______________________________________________________________________

## Scale by running the Research Studio App in the Cloud

Below, we are about to train a 1B+ LLM Model with multi-node.

```bash
python -m lightning run app app.py --cloud
```

Connect to the App once ready.

```
python -m lightning connect {APP_NAME} -y
```

Find below an example with a 1.6B parameter GPT2 transformer model using Lightning Transformers and DeepSpeed using the [Lightning Transformers](https://github.com/Lightning-AI/lightning-transformers) library.

```python
import pytorch_lightning as pl
from lightning_transformers.task.nlp.language_modeling import LanguageModelingDataModule, LanguageModelingTransformer
from transformers import AutoTokenizer

model_name = "gpt2-xl"

tokenizer = AutoTokenizer.from_pretrained(model_name)

model = LanguageModelingTransformer(
    pretrained_model_name_or_path=model_name,
    tokenizer=tokenizer,
    deepspeed_sharding=True,
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

Run your first  multi node training experiment from [sweep_examples/scripts](./sweep_examples/scripts) folder (2 nodes of 4 V100 GPUS each).

```bash
python -m lightning run experiment big_model.py --requirements deepspeed lightning-transformers==0.2.3 --num_nodes=2 --cloud_compute=gpu-fast-multi --disk_size=80
```
