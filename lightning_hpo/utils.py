import os
import shutil
import tarfile
from typing import Optional

from lightning import LightningFlow
from lightning.app.storage import Path
from optuna.distributions import CategoricalDistribution, LogUniformDistribution, UniformDistribution

from lightning_hpo.framework import _OBJECTIVE_FRAMEWORK


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


def _resolve_objective_cls(objective_cls, distributions, framework: str):
    if objective_cls and distributions:
        raise Exception(
            "The arguments `distributions` and `objective_cls` are mutually exclusive. "
            "Please, select which one to use."
        )

    if objective_cls is None:
        if framework not in _OBJECTIVE_FRAMEWORK:
            raise Exception(f"The supported framework are {list(_OBJECTIVE_FRAMEWORK)}. Found {framework}.")
        objective_cls = _OBJECTIVE_FRAMEWORK[framework]

    return objective_cls
