from lightning_hpo.framework.pytorch_lightning import ObjectiveLightningTrainingComponent
from lightning_hpo.objective import BaseObjective

_OBJECTIVE_FRAMEWORK = {
    "base": BaseObjective,
    "pytorch_lightning": ObjectiveLightningTrainingComponent
}