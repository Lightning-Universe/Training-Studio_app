from lightning_hpo.framework.agnostic import BaseObjective
from lightning_hpo.framework.pytorch_lightning import ObjectiveLightningTrainingComponent

_OBJECTIVE_FRAMEWORK = {"base": BaseObjective, "pytorch_lightning": ObjectiveLightningTrainingComponent}
