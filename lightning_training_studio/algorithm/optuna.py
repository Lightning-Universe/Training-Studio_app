import logging
from typing import Any, Dict, List, Optional, Tuple

import optuna
from lightning_utilities.core.apply_func import apply_to_collection
from optuna import create_study, Study, Trial
from optuna.distributions import (
    BaseDistribution,
    CategoricalDistribution,
    IntUniformDistribution,
    LogUniformDistribution,
    UniformDistribution,
)

from lightning_training_studio.algorithm.base import Algorithm
from lightning_training_studio.distributions import DistributionDict
from lightning_training_studio.distributions.distributions import Distribution

_logger = logging.getLogger(__name__)

_DISTRIBUTION_TO_OPTUNA = {
    "uniform": UniformDistribution,
    "int_uniform": IntUniformDistribution,
    "log_uniform": LogUniformDistribution,
    "categorical": CategoricalDistribution,
}


class OptunaAlgorithm(Algorithm):
    def __init__(self, study: Optional[Study] = None, direction: Optional[str] = "minimize") -> None:
        self.study = study or create_study(direction=direction)
        self.experiments: Dict[int, Trial] = {}
        self.reports = {}
        self.distributions: Dict[str, BaseDistribution] = {}

    def register_distributions(self, distributions: Dict[str, DistributionDict]):
        for var_name, distribution in distributions.items():
            distribution_cls = _DISTRIBUTION_TO_OPTUNA[distribution["distribution"]]
            distribution = distribution_cls(**distribution["params"])
            self.distributions[var_name] = distribution

    def register_experiments(self, experiments_config: List[Dict]) -> None:
        for experiment_config in experiments_config:
            trial = optuna.trial.create_trial(
                params=experiment_config["params"],
                distributions=self.distributions,
                value=experiment_config["best_model_score"],
            )
            self.study.add_trial(trial)

    def experiment_start(self, experiment_id: int) -> None:
        if experiment_id not in self.experiments:
            self.experiments[experiment_id] = self.study.ask(self.distributions)

    def experiment_end(self, experiment_id: int, score: float):
        try:
            self.study.tell(experiment_id, score)
        except RuntimeError as e:
            # The trial has already been added to the study.
            print(e)
            pass

        _logger.info(
            f"Experiment {experiment_id} finished with value: {score} and parameters: {self.experiments[experiment_id].params}. "  # noqa: E501
            f"Best is experiment {self.study.best_trial.number} with value: {self.study.best_trial.value}."
        )

    def should_prune(self, experiment_id: int, reports: List[Tuple[float, int]]) -> bool:
        trial = self.experiments[experiment_id]
        if experiment_id not in self.reports:
            self.reports[experiment_id] = []

        for report in reports:
            if report in self.reports[experiment_id]:
                continue
            trial.report(*report)
            self.reports[experiment_id].append(report)

            if trial.should_prune():
                _logger.info(f"Trial {experiment_id} pruned.")
                return True

        return False

    def get_params(self, experiment_id: int) -> Dict[str, Any]:
        params = self.experiments[experiment_id].params
        out = {}
        for k, v in params.items():
            if isinstance(v, float) and v == int(v):
                out[k] = int(v)
            else:
                out[k] = v
        return out


class GridSearch(Algorithm):
    def __init__(self, search_space: Dict[str, Any]):
        sampler = optuna.samplers.GridSampler(search_space)
        self.experiments = {
            i: {n: v for n, v in zip(sampler._param_names, sampler._all_grids[i])}
            for i in range(len(sampler._all_grids))
        }

    @property
    def total_experiments(self) -> int:
        return len(self.experiments)

    def experiment_start(self, experiment_id: int) -> None:
        pass

    def register_experiments(self, experiments_config: List[Dict]) -> None:
        pass

    def register_distributions(self, distributions):
        pass

    def get_params(self, experiment_id: int) -> Dict[str, Any]:
        return self.experiments[experiment_id]

    def should_prune(self) -> bool:
        return False

    def experiment_end(self, experiment_id: int, score: float):
        pass


class RandomSearch(Algorithm):
    def __init__(self, distributions: Dict[str, Any]):
        self.study = create_study(sampler=optuna.samplers.RandomSampler())
        self.distributions = {}
        distributions = apply_to_collection(distributions, Distribution, lambda x: x.to_dict())
        self._register_distributions(distributions)
        self.experiments = {}

    def _register_distributions(self, distributions: Dict[str, DistributionDict]):
        for var_name, distribution in distributions.items():
            distribution_cls = _DISTRIBUTION_TO_OPTUNA[distribution["distribution"]]
            distribution = distribution_cls(**distribution["params"])
            self.distributions[var_name] = distribution

    def experiment_start(self, experiment_id: int) -> None:
        self.experiments[experiment_id] = self.study.ask(self.distributions)

    def register_experiments(self, experiments_config: List[Dict]) -> None:
        for experiment_config in experiments_config:
            trial = optuna.trial.create_trial(
                params=experiment_config["params"],
                distributions=self.distributions,
                value=experiment_config["best_model_score"],
            )
            self.study.add_trial(trial)

    def register_distributions(self, distributions):
        pass

    def get_params(self, experiment_id: int) -> Dict[str, Any]:
        params = self.experiments[experiment_id].params
        out = {}
        for k, v in params.items():
            if isinstance(v, float) and v == int(v):
                out[k] = int(v)
            elif isinstance(v, float):
                out[k] = round(v, 7)
            else:
                out[k] = v
        return out

    def should_prune(self) -> bool:
        return False

    def experiment_end(self, experiment_id: int, score: float):
        pass
