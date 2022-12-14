from textwrap import dedent

from lightning import LightningApp
from lightning.app.utilities import frontend

from lightning_training_studio.app.main import TrainingStudio

description = "The Lightning PyTorch Training Studio App is an AI application that uses the Lightning framework to run experiments or sweep with state-of-the-art algorithms, locally or in the cloud."

on_after_connect = dedent(
    """
Run these commands to run your first Sweep:

# Create a new folder
mkdir new_folder && cd new_folder

# Download example script
curl -o train.py https://raw.githubusercontent.com/Lightning-AI/lightning-hpo/master/sweep_examples/scripts/train.py

# Run a sweep
lightning run sweep train.py --model.lr "[0.001, 0.01]" --data.batch "[32, 64]" --algorithm="grid_search"
"""
)

app = LightningApp(
    TrainingStudio(),
    info=frontend.AppInfo(
        title="Lightning PyTorch Training Studio", description=description  # , on_after_connect=on_after_connect
    ),
)
