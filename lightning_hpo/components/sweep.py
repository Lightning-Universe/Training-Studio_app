import uuid
from typing import Any, Dict, List, Optional, Type, Union
from uuid import uuid4

from lightning import BuildConfig, CloudCompute, LightningFlow
from lightning.app.components.python.tracer import Code
from lightning.app.storage.path import Path
from lightning_utilities.core.apply_func import apply_to_collection

from lightning_hpo.algorithm.base import Algorithm
from lightning_hpo.algorithm.optuna import OptunaAlgorithm
from lightning_hpo.commands.sweep.run import SweepConfig, TrialConfig
from lightning_hpo.controllers.controller import ControllerResource
from lightning_hpo.distributions.distributions import Distribution
from lightning_hpo.framework.agnostic import Objective
from lightning_hpo.loggers import LoggerType
from lightning_hpo.utilities.enum import Stage
from lightning_hpo.utilities.utils import (
    _check_stage,
    _resolve_objective_cls,
    get_best_model_path,
    get_best_model_score,
    HPOCloudCompute,
)


class Sweep(LightningFlow, ControllerResource):

    model = SweepConfig

    def __init__(
        self,
        n_trials: int,
        objective_cls: Optional[Type[Objective]] = None,
        simultaneous_trials: int = 1,
        script_args: Optional[Union[list, str]] = None,
        env: Optional[Dict] = None,
        cloud_compute: Optional[HPOCloudCompute] = None,
        script_path: Optional[str] = None,
        algorithm: Optional[Algorithm] = None,
        logger: Optional[str] = "streamlit",
        sweep_id: Optional[str] = None,
        distributions: Optional[Dict[str, Union[Dict, Distribution]]] = None,
        framework: str = "base",
        code: Optional[Code] = None,
        direction: Optional[str] = None,
        trials_done: Optional[int] = 0,
        requirements: Optional[List[str]] = None,
        trials: Optional[Dict[int, Dict]] = None,
        stage: Optional[str] = Stage.NOT_STARTED,
        logger_url: str = "",
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
        # Serialize the distributions
        distributions = apply_to_collection(distributions, Distribution, lambda x: x.to_dict())

        # SweepConfig
        self.sweep_id = sweep_id or str(uuid.uuid4()).split("-")[0]
        self.script_path = script_path
        self.n_trials = n_trials
        self.simultaneous_trials = simultaneous_trials
        self.trials_done = trials_done or 0
        self.requirements = requirements or []
        self.script_args = script_args
        self.distributions = distributions or {}
        self.framework = framework
        self.cloud_compute = getattr(cloud_compute, "name", "default")
        self.num_nodes = getattr(cloud_compute, "count", 1) if cloud_compute else 1
        self.logger = logger
        self.direction = direction
        self.trials = trials or {}
        self.stage = stage
        self.logger_url = logger_url

        self._objective_cls = _resolve_objective_cls(objective_cls, framework)
        self._algorithm = algorithm or OptunaAlgorithm(direction=direction)
        self._logger = LoggerType(logger).get_logger()
        self._logger.connect(self)

        self._kwargs = {
            "script_path": script_path,
            "env": env,
            "script_args": script_args,
            "num_nodes": getattr(cloud_compute, "count", 1) if cloud_compute else 1,
            "logger": logger,
            "code": code,
            "sweep_id": self.sweep_id,
            "raise_exception": False,
            **objective_kwargs,
        }
        self._algorithm.register_distributions(self.distributions)
        self._algorithm.register_trials([t for t in trials.values() if t["stage"] == Stage.SUCCEEDED] if trials else [])
        self.restart_count = 0

    def run(self):
        if self.stage in (Stage.SUCCEEDED, Stage.STOPPED):
            return

        if self.trials_done == self.n_trials:
            self.stage = Stage.SUCCEEDED
            return

        for trial_id in range(self.num_trials):

            objective = self._get_objective(trial_id)

            if objective:

                if _check_stage(objective, Stage.NOT_STARTED):
                    self._algorithm.trial_start(trial_id)
                    self._logger.on_after_trial_start(self.sweep_id)

                if not self.trials[trial_id]["params"]:
                    self.stage = Stage.RUNNING
                    self.trials[trial_id]["params"] = self._algorithm.get_params(trial_id)

                logger_url = self._logger.get_url(trial_id)
                if logger_url is not None and self.logger_url != logger_url:
                    self.logger_url = logger_url

                objective.run(
                    params=self._algorithm.get_params(trial_id),
                    restart_count=self.restart_count,
                )

                self.trials[trial_id]["progress"] = objective.progress

                if _check_stage(objective, Stage.FAILED):
                    self.trials[trial_id]["stage"] = Stage.FAILED
                    self.trials[trial_id]["exception"] = objective.status.message
                    objective.stop()

                if objective.reports and not self.trials[trial_id]["stage"] == "pruned":
                    if self._algorithm.should_prune(trial_id, objective.reports):
                        self.trials[trial_id]["stage"] = Stage.PRUNED
                        objective.stop()
                        self.trials_done += 1
                        continue

                if self.stage != Stage.FAILED and self.trials[trial_id]["stage"] == Stage.PENDING:
                    if self.trials[trial_id]["stage"] != objective.status:
                        self.stage = Stage.RUNNING
                        self.trials[trial_id]["stage"] = Stage.RUNNING

                if objective.best_model_score:
                    if self.trials[trial_id]["stage"] == Stage.SUCCEEDED:
                        pass
                    elif self.trials[trial_id]["stage"] not in (Stage.PRUNED, Stage.STOPPED, Stage.FAILED):
                        self._algorithm.trial_end(trial_id, objective.best_model_score)
                        self._logger.on_after_trial_end(
                            sweep_id=self.sweep_id,
                            trial_id=objective.trial_id,
                            monitor=objective.monitor,
                            score=objective.best_model_score,
                            params=self._algorithm.get_params(trial_id),
                        )
                        self.trials[trial_id]["best_model_score"] = objective.best_model_score
                        self.trials[trial_id]["best_model_path"] = str(objective.best_model_path)
                        self.trials[trial_id]["monitor"] = objective.monitor
                        self.trials[trial_id]["stage"] = Stage.SUCCEEDED
                        self.trials_done += 1
                        objective.stop()

        if all(self.trials[trial_id]["stage"] == Stage.FAILED for trial_id in range(self.num_trials)):
            self.stage = Stage.FAILED

    @property
    def num_trials(self) -> int:
        return min(self.trials_done + self.simultaneous_trials, self.n_trials)

    @property
    def best_model_score(self) -> Optional[float]:
        return get_best_model_score(self)

    @property
    def best_model_path(self) -> Optional[Path]:
        return get_best_model_path(self)

    def stop_trial(self, trial_id: int):
        objective = self._get_objective(trial_id)
        if objective:
            objective.stop()
            self.trials[trial_id]["stage"] = Stage.STOPPED
            self.trials_done += 1

    def _get_objective(self, trial_id: int):
        trial_config = self.trials.get(trial_id, None)
        if trial_config is None:
            trial_config = TrialConfig(
                name=str(uuid4()).split("-")[-1],
                best_model_score=None,
                monitor=None,
                best_model_path=None,
                stage=Stage.PENDING,
                params={},
            ).dict()
            self.trials[trial_id] = trial_config

        if trial_config["stage"] == Stage.SUCCEEDED:
            return

        objective = getattr(self, f"w_{trial_id}", None)
        if objective is None:
            cloud_compute = CloudCompute(name=self.cloud_compute if self.cloud_compute else "cpu")
            objective = self._objective_cls(trial_id=trial_id, cloud_compute=cloud_compute, **self._kwargs)
            setattr(self, f"w_{trial_id}", objective)
        return objective

    @classmethod
    def from_config(cls, config: SweepConfig, code: Optional[Code] = None):
        return cls(
            script_path=config.script_path,
            n_trials=config.n_trials,
            simultaneous_trials=config.simultaneous_trials,
            framework=config.framework,
            script_args=config.script_args,
            trials_done=config.trials_done,
            distributions={k: v.dict() for k, v in config.distributions.items()},
            cloud_compute=HPOCloudCompute(config.cloud_compute, config.num_nodes),
            sweep_id=config.sweep_id,
            code=code,
            cloud_build_config=BuildConfig(requirements=config.requirements),
            logger=config.logger,
            algorithm=OptunaAlgorithm(direction=config.direction),
            trials={k: v.dict() for k, v in config.trials.items()},
            direction=config.direction,
            stage=config.stage,
            logger_url=config.logger_url,
        )

    def configure_layout(self):
        return self._logger.configure_layout()
