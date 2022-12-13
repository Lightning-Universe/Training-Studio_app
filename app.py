from textwrap import dedent

from lightning import LightningApp
from lightning.app.utilities import frontend

from lightning_training_studio.app.main import TrainingStudio

description = dedent(
    """
The Lightning PyTorch Training Studio App is a full-stack AI application
built using the Lightning framework enabling to run experiments or sweep
with SOTA hyper-parameters algorithms locally or in the cloud.
"""
)

on_after_connect = dedent(
    """
Run those commands to run your first Sweep:

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
        title="Lightning PyTorch Training Studio", description=description, on_after_connect=on_after_connect
    ),
)
