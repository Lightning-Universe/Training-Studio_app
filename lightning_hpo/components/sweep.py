import uuid
from typing import Any, Dict, List, Optional, Type, Union

from lightning import BuildConfig, CloudCompute, LightningFlow
from lightning.app.components.python.tracer import Code
from lightning.app.storage.path import Path

from lightning_hpo.algorithm.base import Algorithm
from lightning_hpo.algorithm.optuna import OptunaAlgorithm
from lightning_hpo.commands.sweep.run import Params, SweepConfig, TrialConfig
from lightning_hpo.distributions import Distribution
from lightning_hpo.distributions.distributions import parse_distributions, unparse_distributions
from lightning_hpo.framework.agnostic import Objective
from lightning_hpo.loggers import LoggerType
from lightning_hpo.utilities.enum import Status
from lightning_hpo.utilities.utils import (
    _check_status,
    _resolve_objective_cls,
    get_best_model_path,
    get_best_model_score,
    HPOCloudCompute,
)


class Sweep(LightningFlow):
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
        logger: str = "streamlit",
        sweep_id: Optional[str] = None,
        distributions: Optional[Dict[str, Distribution]] = None,
        framework: str = "base",
        code: Optional[Code] = None,
        direction: Optional[str] = None,
        trials_done: Optional[int] = 0,
        requirements: Optional[List[str]] = None,
        trials: Optional[Dict[int, TrialConfig]] = None,
        status: Optional[str] = Status.NOT_STARTED,
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
        # Sweep Database Spec
        self._sweep_config = SweepConfig(
            sweep_id=sweep_id or str(uuid.uuid4()).split("-")[0],
            script_path=script_path,
            n_trials=n_trials,
            simultaneous_trials=simultaneous_trials,
            trials_done=trials_done,
            requirements=requirements or [],
            script_args=script_args,
            distributions=unparse_distributions(distributions),
            framework=framework,
            cloud_compute=getattr(cloud_compute, "name", "default"),
            num_nodes=getattr(cloud_compute, "count", 1) if cloud_compute else 1,
            logger=logger,
            direction=direction,
            trials=trials or {},
            status=status,
        )

        self._objective_cls = _resolve_objective_cls(objective_cls, framework)

        self._algorithm = algorithm or OptunaAlgorithm(direction=direction)
        self._logger = LoggerType(logger).get_logger()
        self._logger.connect(self)

        self._kwargs = {
            "script_path": script_path,
            "env": env,
            "script_args": script_args,
            "cloud_compute": CloudCompute(name=cloud_compute.name if cloud_compute else "cpu"),
            "num_nodes": getattr(cloud_compute, "count", 1) if cloud_compute else 1,
            "logger": logger,
            "code": code,
            "sweep_id": self._sweep_config.sweep_id,
            "raise_exception": False,
            **objective_kwargs,
        }
        self._algorithm.register_distributions(
            {k: d.to_dict() if isinstance(d, Distribution) else d for k, d in (distributions or {}).items()}
        )
        self._algorithm.register_trials([t for t in trials.values() if t.status == Status.SUCCEEDED] if trials else [])
        self.restart_count = 0
        self.has_updated = False
        self.sweep = False
        self.show = False

    def run(self):
        if self._sweep_config.status in (Status.FAILED, Status.SUCCEEDED, Status.STOPPED):
            return

        if self._sweep_config.trials_done == self._sweep_config.n_trials:
            self._sweep_config.status = Status.SUCCEEDED
            self.has_updated = True
            return

        for trial_id in range(self._sweep_config.num_trials):

            objective = self._get_objective(trial_id)

            if objective:

                if _check_status(objective, Status.NOT_STARTED):
                    self._algorithm.trial_start(trial_id)
                    self._logger.on_after_trial_start(self._sweep_config.sweep_id)

                if not self._sweep_config.trials[trial_id].params.params:
                    self._sweep_config.status = Status.RUNNING
                    self._sweep_config.trials[trial_id].params = Params(params=self._algorithm.get_params(trial_id))
                    self.has_updated = True

                objective.run(
                    params=self._algorithm.get_params(trial_id),
                    restart_count=self.restart_count,
                )

                if _check_status(objective, Status.FAILED):
                    self._sweep_config.status = Status.FAILED
                    self._sweep_config.trials[trial_id].status = Status.FAILED
                    self.has_updated = True

                if objective.reports and not self._sweep_config.trials[trial_id].pruned:
                    if self._algorithm.should_prune(trial_id, objective.reports):
                        self._sweep_config.trials[trial_id].status = Status.PRUNED
                        self.has_updated = True
                        objective.stop()
                        continue

                if objective.best_model_score and not objective.has_stopped and not objective.pruned:
                    self._algorithm.trial_end(trial_id, objective.best_model_score)
                    self._logger.on_after_trial_end(
                        sweep_id=self._sweep_config.sweep_id,
                        trial_id=objective.trial_id,
                        monitor=objective.monitor,
                        score=objective.best_model_score,
                        params=self._algorithm.get_params(trial_id),
                    )
                    self._sweep_config.trials[trial_id].best_model_score = objective.best_model_score
                    self._sweep_config.trials[trial_id].best_model_path = objective.best_model_path
                    self._sweep_config.trials[trial_id].monitor = objective.monitor
                    self._sweep_config.trials[trial_id].status = Status.SUCCEEDED
                    self._sweep_config.trials_done += 1
                    self.has_updated = True
                    objective.stop()

    @property
    def best_model_score(self) -> Optional[float]:
        return get_best_model_score(self)

    @property
    def best_model_path(self) -> Optional[Path]:
        return get_best_model_path(self)

    def configure_layout(self):
        return self._logger.configure_layout()

    def _get_objective(self, trial_id: int):
        trial_config = self._sweep_config.trials.get(trial_id, None)
        if trial_config is None:
            trial_config = TrialConfig(
                best_model_score=None,
                monitor=None,
                best_model_path=None,
                status=Status.PENDING,
                params=Params(params={}),
            )
            self._sweep_config.trials[trial_id] = trial_config

        if trial_config.status == Status.SUCCEEDED:
            return

        objective = getattr(self, f"w_{trial_id}", None)
        if objective is None:
            objective = self._objective_cls(trial_id=trial_id, **self._kwargs)
            setattr(self, f"w_{trial_id}", objective)
        return objective

    @property
    def updates(self) -> List[SweepConfig]:
        res = []
        if self.has_updated:
            res = [self._sweep_config]
        self.has_updated = False
        return res

    @classmethod
    def from_config(cls, config: SweepConfig, code: Optional[Code] = None):
        return cls(
            script_path=config.script_path,
            n_trials=config.n_trials,
            simultaneous_trials=config.simultaneous_trials,
            framework=config.framework,
            script_args=config.script_args,
            trials_done=config.trials_done,
            distributions=parse_distributions(config.distributions),
            cloud_compute=HPOCloudCompute(config.cloud_compute, config.num_nodes),
            sweep_id=config.sweep_id,
            code=code,
            cloud_build_config=BuildConfig(requirements=config.requirements),
            logger=config.logger,
            algorithm=OptunaAlgorithm(direction=config.direction),
            trials=config.trials,
            direction=config.direction,
            status=config.status,
        )
