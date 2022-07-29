import os
import shutil
import tarfile
from dataclasses import dataclass
from typing import Optional, Union

from lightning import CloudCompute as LightningCloudCompute
from lightning import LightningFlow
from lightning.app.storage import Path
from lightning.app.utilities.enum import WorkStageStatus
from optuna.distributions import CategoricalDistribution, LogUniformDistribution, UniformDistribution

from lightning_hpo.framework import _OBJECTIVE_FRAMEWORK
from lightning_hpo.framework.agnostic import BaseObjective


@dataclass
class CloudCompute(LightningCloudCompute):
    count: int = 1


def config_to_distributions(config):
    distributions = {}
    mapping_name_to_cls = {
        "categorical": CategoricalDistribution,
        "uniform": UniformDistribution,
        "log_uniform": LogUniformDistribution,
    }
    for k, v in config.distributions.items():
        dist_cls = mapping_name_to_cls[v.pop("distribution")]
        distributions[k] = dist_cls(**v)
    return distributions


def get_best_model_score(flow: LightningFlow) -> Optional[float]:
    metrics = [work.best_model_score for work in flow.works()]
    if not all(metrics):
        return None
    return max(metrics)


def get_best_model_path(flow: LightningFlow) -> Optional[Path]:
    metrics = {work.best_model_score: work for work in flow.works()}
    if not all(metrics):
        return None

    if all(metric is None for metric in metrics):
        return None

    return metrics[max(metrics)].best_model_path


def clean_tarfile(file_path: str, mode):
    if os.path.exists(file_path):
        with tarfile.open(file_path, mode=mode) as tar_ref:
            for member in tar_ref.getmembers():
                p = member.path
                if p != "." and os.path.exists(p):
                    if os.path.isfile(p):
                        os.remove(p)
                    else:
                        shutil.rmtree(p)
        os.remove(file_path)


def extract_tarfile(file_path: str, extract_path: str, mode: str):
    if os.path.exists(file_path):
        with tarfile.open(file_path, mode=mode) as tar_ref:
            for member in tar_ref.getmembers():
                try:
                    tar_ref.extract(member, path=extract_path, set_attrs=False)
                except PermissionError:
                    raise PermissionError(f"Could not extract tar file {file_path}")


def _resolve_objective_cls(objective_cls, framework: str):
    if objective_cls is None:
        if framework not in _OBJECTIVE_FRAMEWORK:
            raise Exception(f"The supported framework are {list(_OBJECTIVE_FRAMEWORK)}. Found {framework}.")
        objective_cls = _OBJECTIVE_FRAMEWORK[framework]

    return objective_cls


def _check_status(obj: Union[LightningFlow, BaseObjective], status: str) -> bool:
    if isinstance(obj, BaseObjective):
        return obj.status.stage == status
    else:
        works = obj.works()
        if works:
            return any(w.status.stage == status for w in obj.works())
        else:
            return status == WorkStageStatus.NOT_STARTED


def _calculate_next_num_trials(num_trials: int, n_trials: int, simultaneous_trials: int) -> int:
    if num_trials == n_trials:
        num_trials += 1
    elif num_trials >= (n_trials - simultaneous_trials):
        num_trials = n_trials
    else:
        num_trials += simultaneous_trials
    return num_trials
