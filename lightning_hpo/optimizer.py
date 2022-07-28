import uuid
from typing import Any, Dict, Optional, Type, Union

import optuna
from lightning import CloudCompute, LightningFlow
from lightning.app.components.python.tracer import Code
from lightning.app.storage.path import Path
from lightning.app.utilities.enum import WorkStageStatus

from lightning_hpo.framework.agnostic import BaseObjective
from lightning_hpo.loggers import LoggerType
from lightning_hpo.utils import _resolve_objective_cls


class Optimizer(LightningFlow):
    def __init__(
        self,
        n_trials: int,
        objective_cls: Optional[Type[BaseObjective]] = None,
        simultaneous_trials: int = 1,
        script_args: Optional[Union[list, str]] = None,
        env: Optional[Dict] = None,
        cloud_compute: Optional[CloudCompute] = None,
        script_path: Optional[str] = None,
        study: Optional[optuna.Study] = None,
        logger: str = "streamlit",
        sweep_id: Optional[str] = None,
        distributions: Optional[Dict[str, optuna.distributions.BaseDistribution]] = None,
        framework: str = "base",
        code: Optional[Code] = None,
        **objective_kwargs: Any,
    ):
        """The Optimizer class enables to easily run a Python Script with Lightning
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
        self._objective_cls = _resolve_objective_cls(objective_cls, distributions, framework)
        self.n_trials = n_trials
        self.num_trials = self.simultaneous_trials = simultaneous_trials
        self.sweep_id = sweep_id or str(uuid.uuid4()).split("-")[0]
        self._study = study or optuna.create_study()
        self._logger = LoggerType(logger).get_logger()
        self._logger.connect(self)
        self._kwargs = {
            "script_path": script_path,
            "env": env,
            "script_args": script_args,
            "cloud_compute": cloud_compute,
            "logger": logger,
            "code": code,
            "sweep_id": self.sweep_id,
            "raise_exception": False,
            **objective_kwargs,
        }
        self._trials = {}
        self._distributions = distributions
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
            objective = getattr(self, f"w_{trial_id}", None)
            if objective is None:
                objective = self._objective_cls(trial_id=trial_id, **self._kwargs)
                setattr(self, f"w_{trial_id}", objective)

            if self._check_status(objective, WorkStageStatus.NOT_STARTED):
                trial = self._study.ask(self._distributions)
                self._trials[trial_id] = trial
                self._logger.on_trial_start(self.sweep_id)

            objective.run(params=self._trials[trial_id].params, restart_count=self.restart_count)

            if self._check_status(objective, WorkStageStatus.FAILED):
                self.has_failed = True

            if objective.reports and not objective.pruned:
                trial = self._trials[objective.trial_id]
                for report in objective.reports:
                    if report not in objective.flow_reports:
                        trial.report(*report)
                        objective.flow_reports.append(report)
                    if trial.should_prune():
                        print(f"Trial {trial_id} pruned.")
                        objective.pruned = True
                        objective.stop()
                        break

            if objective.best_model_score and not objective.has_stopped and not objective.pruned:
                self._study.tell(objective.trial_id, objective.best_model_score)
                self._logger.on_trial_end(
                    sweep_id=self.sweep_id,
                    trial_id=objective.trial_id,
                    monitor=objective.monitor,
                    score=objective.best_model_score,
                    params=objective.params,
                )
                objective.stop()

                print(
                    f"Trial {trial_id} finished with value: {objective.best_model_score} and parameters: {objective.params}. "  # noqa: E501
                    f"Best is trial {self._study.best_trial.number} with value: {self._study.best_trial.value}."
                )

            has_told_study.append(objective.has_stopped)

        if all(has_told_study):
            if self.num_trials == self.n_trials:
                self.num_trials += 1
            elif self.num_trials >= (self.n_trials - self.simultaneous_trials):
                self.num_trials = self.n_trials
            else:
                self.num_trials += self.simultaneous_trials

    @property
    def best_model_score(self) -> Optional[float]:
        metrics = [work.best_model_score for work in self.works()]
        if not all(metrics):
            return None
        return max(metrics)

    @property
    def best_model_path(self) -> Optional[Path]:
        metrics = [work.best_model_score for work in self.works()]
        if not all(metrics):
            return None
        for trial_id, metric in enumerate(metrics):
            if metric == self.best_model_score:
                return getattr(self, f"w_{trial_id}").best_model_path

    def configure_layout(self):
        return self._logger.configure_layout()

    def _check_status(self, obj: Union[LightningFlow, BaseObjective], status: str) -> bool:
        if isinstance(obj, BaseObjective):
            return obj.status.stage == status
        else:
            works = obj.works()
            if works:
                return any(w.status.stage == status for w in obj.works())
            else:
                return status == WorkStageStatus.NOT_STARTED
