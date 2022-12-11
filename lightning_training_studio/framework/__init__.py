from lightning_training_studio.framework.agnostic import Objective
from lightning_training_studio.framework.pytorch_lightning import ObjectiveLightningTrainingComponent

_OBJECTIVE_FRAMEWORK = {"base": Objective, "pytorch_lightning": ObjectiveLightningTrainingComponent}
