import uuid
from typing import Any, Dict, List, Optional, Type, Union

from lightning import BuildConfig, LightningFlow
from lightning.app.components.python.tracer import Code
from lightning.app.storage.path import Path
from lightning.app.utilities.enum import WorkStageStatus

from lightning_hpo.algorithm.base import Algorithm
from lightning_hpo.algorithm.optuna import OptunaAlgorithm
from lightning_hpo.commands.sweep import SweepConfig
from lightning_hpo.components.servers.db.models import Trial
from lightning_hpo.distributions import Distribution
from lightning_hpo.distributions.distributions import parse_distributions
from lightning_hpo.framework.agnostic import BaseObjective
from lightning_hpo.loggers import LoggerType
from lightning_hpo.utilities.utils import (
    _calculate_next_num_trials,
    _check_status,
    _resolve_objective_cls,
    CloudCompute,
    get_best_model_path,
    get_best_model_score,
)


class Sweep(LightningFlow):
    def __init__(
        self,
        n_trials: int,
        objective_cls: Optional[Type[BaseObjective]] = None,
        simultaneous_trials: int = 1,
        script_args: Optional[Union[list, str]] = None,
        env: Optional[Dict] = None,
        cloud_compute: Optional[CloudCompute] = None,
        script_path: Optional[str] = None,
        algorithm: Optional[Algorithm] = None,
        logger: str = "streamlit",
        sweep_id: Optional[str] = None,
        distributions: Optional[Dict[str, Distribution]] = None,
        framework: str = "base",
        code: Optional[Code] = None,
        direction: Optional[str] = None,
        **objective_kwargs: Any,
    ):
        """The Sweep class enables to easily run a Python Script with Lightning
        :class:`~lightning.utilities.tracer.Tracer` with state-of-the-art distributed.
        Arguments:
            n_trials: Number of HPO trials to run.
            objective_cls: Your custom base objective work.
            simultaneous_trials: Number of parallel trials to run.
            script_args: Optional script arguments.
            env: Environment variables to be passed to the script.
            cloud_compute: The cloud compute on which the Work should run on.
            blocking: Whether the Work should be blocking or asynchronous.
            script_path: Path of the python script to run.
            logger: Which logger to use
            objective_kwargs: Your custom keywords arguments passed to your custom objective work class.
        """
        super().__init__()
        self._objective_cls = _resolve_objective_cls(objective_cls, framework)
        self.n_trials = n_trials
        self.num_trials = self.simultaneous_trials = simultaneous_trials
        self.sweep_id = sweep_id or str(uuid.uuid4()).split("-")[0]
        self._algorithm = algorithm or OptunaAlgorithm(direction=direction)
        self._logger = LoggerType(logger).get_logger()
        self._logger.connect(self)
        self._kwargs = {
            "script_path": script_path,
            "env": env,
            "script_args": script_args,
            "cloud_compute": cloud_compute,
            "num_nodes": getattr(cloud_compute, "count", 1) if cloud_compute else 1,
            "logger": logger,
            "code": code,
            "sweep_id": self.sweep_id,
            "raise_exception": False,
            **objective_kwargs,
        }
        self._algorithm.register_distributions(
            {k: d.to_dict() if isinstance(d, Distribution) else d for k, d in (distributions or {}).items()}
        )
        self.has_failed = False
        self.restart_count = 0
        self.show = False

    def run(self):
        if self.has_failed:
            return

        if self.num_trials > self.n_trials:
            return

        has_told_study = []

        for trial_id in range(self.num_trials):
            objective = self._get_objective(trial_id)

            if _check_status(objective, WorkStageStatus.NOT_STARTED):
                self._algorithm.trial_start(trial_id)
                self._logger.on_after_trial_start(self.sweep_id)

            objective.run(params=self._algorithm.get_params(trial_id), restart_count=self.restart_count)

            if _check_status(objective, WorkStageStatus.FAILED):
                self.has_failed = True

            if objective.reports and not objective.pruned:
                if self._algorithm.should_prune(trial_id, objective.reports):
                    objective.pruned = True
                    objective.stop()
                    break

            if objective.best_model_score and not objective.has_stopped and not objective.pruned:
                self._algorithm.trial_end(trial_id, objective.best_model_score)
                self._logger.on_after_trial_end(
                    sweep_id=self.sweep_id,
                    trial_id=objective.trial_id,
                    monitor=objective.monitor,
                    score=objective.best_model_score,
                    params=self._algorithm.get_params(trial_id),
                )
                objective.stop()

            has_told_study.append(objective.has_stopped)

        if all(has_told_study):
            self.num_trials = _calculate_next_num_trials(self.num_trials, self.n_trials, self.simultaneous_trials)

    @property
    def best_model_score(self) -> Optional[float]:
        return get_best_model_score(self)

    @property
    def best_model_path(self) -> Optional[Path]:
        return get_best_model_path(self)

    def configure_layout(self):
        return self._logger.configure_layout()

    def _get_objective(self, trial_id: int):
        objective = getattr(self, f"w_{trial_id}", None)
        if objective is None:
            objective = self._objective_cls(trial_id=trial_id, **self._kwargs)
            setattr(self, f"w_{trial_id}", objective)
        return objective

    def get_trials(self) -> List[Trial]:
        trials = []
        for trial_id in range(self.num_trials):
            objective = getattr(self, f"w_{trial_id}", None)
            if objective and (objective.has_stopped or objective.has_failed) and not objective.has_stored:
                trial = Trial(
                    sweep_id=self.sweep_id,
                    trial_id=trial_id,
                    best_model_score=objective.best_model_score,
                    monitor=objective.monitor,
                    name=objective.name,
                    best_model_path=str(objective.best_model_path),
                    has_succeeded=not objective.has_failed,
                    url=self._logger.get_url(trial_id),
                    params=str(objective.params),
                )
                objective.has_stored = True
                trials.append(trial)
        return trials

    @classmethod
    def from_config(cls, config: SweepConfig, code: Optional[Code] = None):
        return cls(
            script_path=config.script_path,
            n_trials=config.n_trials,
            simultaneous_trials=config.simultaneous_trials,
            framework=config.framework,
            script_args=config.script_args,
            distributions=parse_distributions(config.distributions),
            cloud_compute=CloudCompute(config.cloud_compute, config.num_nodes),
            sweep_id=config.sweep_id,
            code=code,
            cloud_build_config=BuildConfig(requirements=config.requirements),
            logger=config.logger,
            algorithm=OptunaAlgorithm(direction=config.direction),
        )
