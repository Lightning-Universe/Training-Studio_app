from lightning_hpo.framework.agnostic import Objective
from lightning_hpo.framework.pytorch_lightning import ObjectiveLightningTrainingComponent

_OBJECTIVE_FRAMEWORK = {"base": Objective, "pytorch_lightning": ObjectiveLightningTrainingComponent}
