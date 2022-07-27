from lightning import LightningFlow, CloudCompute, LightningWork
import optuna
import os
from lightning_hpo.hyperplot import HiPlotFlow
from typing import Optional, Union, Dict, Type, Any
from lightning.app.storage.path import Path
from lightning.app.utilities.enum import WorkStageStatus
from lightning_hpo.loggers import Loggers, WandbConfig
from typing import List
from lightning_hpo.framework import _OBJECTIVE_FRAMEWORK
from lightning.app.components.python.tracer import Code

class Optimizer(LightningFlow):

    def __init__(
        self,
        n_trials: int,
        simultaneous_trials: int = 1,
        script_args: Optional[Union[list, str]] = None,
        objective_cls: Optional[Type[Any]] = None,
        framework: str = "pytorch_lightning",
        distributions: Optional[Dict[str, optuna.distributions.BaseDistribution]] = None,
        cloud_compute: Optional[CloudCompute] = None,
        script_path: Optional[str] = None,
        study: Optional[optuna.Study] = None,
        logger: str = "streamlit",
        code: Optional[Code] = None,
        sweep_id: Optional[str] = None,
        **objective_work_kwargs: Any,
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
            objective_work_kwargs: Your custom keywords arguments passed to your custom objective work class.
        """
        super().__init__()
        if objective_cls and distributions:
            raise Exception(
                "The arguments `distributions` and `objective_cls` are mutually exclusive. "
                "Please, select which one to use."
            )

        if objective_cls is None:
            if framework not in self.supported_frameworks():
                raise Exception(f"The supported framework are {self.supported_frameworks()}. Found {framework}.")
            objective_cls = _OBJECTIVE_FRAMEWORK[framework]

        self.n_trials = n_trials
        self.simultaneous_trials = simultaneous_trials
        self.num_trials = simultaneous_trials
        self._study = study or optuna.create_study()
        self.sweep_id = sweep_id

        if logger == Loggers.STREAMLIT:
            self.hi_plot = HiPlotFlow()
        elif logger == Loggers.WANDB:
            self.hi_plot = None
            WandbConfig.validate()

        for trial_id in range(n_trials):
            objective_work = objective_cls(
                script_path=script_path,
                script_args=script_args,
                cloud_compute=cloud_compute,
                code=code,
                sweep_id=sweep_id,
                trial_id=trial_id,
                logger=logger,
                **objective_work_kwargs,
            )
            setattr(self, f"w_{trial_id}", objective_work)

        self._trials = {}
        self._distributions = distributions or objective_work.distributions()
        self.has_failed = False
        self.restart_count = 0

    def run(self):
        if self.has_failed:
            return

        if self.num_trials > self.n_trials:
            return

        has_told_study = []

        for trial_idx in range(self.num_trials):
            objective = getattr(self, f"w_{trial_idx}")

            if self.check_status(objective, WorkStageStatus.NOT_STARTED):
                trial = self._study.ask(self._distributions)
                self._trials[trial_idx] = trial

            objective.run(
                params=self._trials[trial_idx].params,
                restart_count=self.restart_count,
            )

            if self.check_status(objective, "failed"):
                self.has_failed = True

            if getattr(objective, "reports", None) and not objective.pruned:
                trial = self._trials[objective.trial_id]
                for report in objective.reports:
                    if report not in objective.flow_reports:
                        trial.report(*report)
                        objective.flow_reports.append(report)

                    if trial.should_prune():
                        print(f"Trail {trial_idx} pruned.")
                        objective.pruned = True
                        objective.stop()
                        break

            if objective.best_model_score and not objective.has_stopped and not objective.pruned:
                # TODO: Understand why this is failing.
                try:
                    self._study.tell(objective.trial_id, objective.best_model_score)
                except RuntimeError:
                    pass
                if self.hi_plot:
                    self.hi_plot.data.append({"x": objective.best_model_score, **objective.params})
                objective.stop()
                print(
                    f"Trial {trial_idx} finished with value: {objective.best_model_score} and parameters: {objective.params}. "
                    f"Best is trial {self._study.best_trial.number} with value: {self._study.best_trial.value}."
                )

            has_told_study.append(objective.has_stopped)

        if all(has_told_study):
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
        for trial_idx, metric in enumerate(metrics):
            if metric == self.best_model_score:
                return getattr(self, f"w_{trial_idx}").best_model_path

    def configure_layout(self):
        if self.hi_plot:
            content = self.hi_plot
        else:
            content = f"https://wandb.ai/{os.getenv('WANDB_ENTITY')}/{self.sweep_id}"
        return [{"name": "Experiment", "content": content}]

    @staticmethod
    def supported_frameworks() -> List[str]:
        return list(_OBJECTIVE_FRAMEWORK.keys())

    def check_status(self, obj: Union[LightningFlow, LightningWork], status: str) -> bool:
        if isinstance(obj, LightningWork):
            return obj.status.stage == status
        else:
            works = obj.works()
            if works:
                return any(w.status.stage == status for w in obj.works())
            else:
                return status == WorkStageStatus.NOT_STARTED