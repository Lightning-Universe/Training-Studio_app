import logging
from typing import Any, Dict, List, Optional, Tuple

import optuna
from optuna import create_study, Study, Trial
from optuna.distributions import (
    BaseDistribution,
    CategoricalDistribution,
    IntUniformDistribution,
    LogUniformDistribution,
    UniformDistribution,
)

from lightning_hpo.algorithm.base import Algorithm
from lightning_hpo.commands.sweep.run import TrialConfig
from lightning_hpo.distributions import DistributionDict

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

    def register_trials(self, trials_config: List[TrialConfig]) -> None:
        for trial_config in trials_config:
            trial = optuna.trial.create_trial(
                params=trial_config.params.params, distributions=self.distributions, value=trial_config.best_model_score
            )
            self.study.add_trial(trial)

    def trial_start(self, trial_id: int) -> None:
        if trial_id not in self.trials:
            self.trials[trial_id] = self.study.ask(self.distributions)

    def trial_end(self, trial_id: int, score: float):
        self.study.tell(trial_id, score)

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
            if v == int(v):
                out[k] = int(v)
            else:
                out[k] = v
        return out
