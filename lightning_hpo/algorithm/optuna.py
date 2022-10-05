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

from lightning_hpo.algorithm.base import Algorithm
from lightning_hpo.distributions import DistributionDict
from lightning_hpo.distributions.distributions import Distribution

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
        self.trials: Dict[int, Trial] = {}
        self.reports = {}
        self.distributions: Dict[str, BaseDistribution] = {}

    def register_distributions(self, distributions: Dict[str, DistributionDict]):
        for var_name, distribution in distributions.items():
            distribution_cls = _DISTRIBUTION_TO_OPTUNA[distribution["distribution"]]
            distribution = distribution_cls(**distribution["params"])
            self.distributions[var_name] = distribution

    def register_trials(self, trials_config: List[Dict]) -> None:
        for trial_config in trials_config:
            trial = optuna.trial.create_trial(
                params=trial_config["params"],
                distributions=self.distributions,
                value=trial_config["best_model_score"],
            )
            self.study.add_trial(trial)

    def trial_start(self, trial_id: int) -> None:
        if trial_id not in self.trials:
            self.trials[trial_id] = self.study.ask(self.distributions)

    def trial_end(self, trial_id: int, score: float):
        try:
            self.study.tell(trial_id, score)
        except RuntimeError as e:
            # The trial has already been added to the study.
            print(e)
            pass

        _logger.info(
            f"Trial {trial_id} finished with value: {score} and parameters: {self.trials[trial_id].params}. "  # noqa: E501
            f"Best is trial {self.study.best_trial.number} with value: {self.study.best_trial.value}."
        )

    def should_prune(self, trial_id: int, reports: List[Tuple[float, int]]) -> bool:
        trial = self.trials[trial_id]
        if trial_id not in self.reports:
            self.reports[trial_id] = []

        for report in reports:
            if report in self.reports[trial_id]:
                continue
            trial.report(*report)
            self.reports[trial_id].append(report)

            if trial.should_prune():
                _logger.info(f"Trial {trial_id} pruned.")
                return True

        return False

    def get_params(self, trial_id: int) -> Dict[str, Any]:
        params = self.trials[trial_id].params
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
        self.trials = {
            i: {n: v for n, v in zip(sampler._param_names, sampler._all_grids[i])}
            for i in range(len(sampler._all_grids))
        }

    def trial_start(self, trial_id: int) -> None:
        pass

    def register_trials(self, trials_config: List[Dict]) -> None:
        pass

    def register_distributions(self, distributions):
        assert not distributions

    def get_params(self, trial_id: int) -> Dict[str, Any]:
        return self.trials[trial_id]

    def should_prune(self) -> bool:
        return False

    def trial_end(self, trial_id: int, score: float):
        pass


class RandomSearch(Algorithm):
    def __init__(self, distributions: Dict[str, Any]):
        self.study = create_study(sampler=optuna.samplers.RandomSampler())
        self.distributions = {}
        distributions = apply_to_collection(distributions, Distribution, lambda x: x.to_dict())
        self._register_distributions(distributions)
        self.trials = {}

    def _register_distributions(self, distributions: Dict[str, DistributionDict]):
        for var_name, distribution in distributions.items():
            distribution_cls = _DISTRIBUTION_TO_OPTUNA[distribution["distribution"]]
            distribution = distribution_cls(**distribution["params"])
            self.distributions[var_name] = distribution

    def trial_start(self, trial_id: int) -> None:
        self.trials[trial_id] = self.study.ask(self.distributions)

    def register_trials(self, trials_config: List[Dict]) -> None:
        for trial_config in trials_config:
            trial = optuna.trial.create_trial(
                params=trial_config["params"],
                distributions=self.distributions,
                value=trial_config["best_model_score"],
            )
            self.study.add_trial(trial)

    def register_distributions(self, distributions):
        assert not distributions

    def get_params(self, trial_id: int) -> Dict[str, Any]:
        params = self.trials[trial_id].params
        out = {}
        for k, v in params.items():
            if isinstance(v, float) and v == int(v):
                out[k] = int(v)
            else:
                out[k] = v
        return out

    def should_prune(self) -> bool:
        return False

    def trial_end(self, trial_id: int, score: float):
        pass
