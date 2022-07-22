from lightning import LightningFlow, LightningWork, CloudCompute
from lightning_hpo.objective import BaseObjective
import optuna
import os
from lightning_hpo.hyperplot import HiPlotFlow
from typing import Optional, Union, Dict, Type, Any
from lightning.app.storage.path import Path
from lightning.app.utilities.enum import WorkStageStatus
from lightning_hpo.config import Loggers
from lightning_hpo.wandb import WandB
import uuid


class Optimizer(LightningFlow):
    def __init__(
        self,
        n_trials: int,
        objective_cls: Type[BaseObjective],
        simultaneous_trials: int = 1,
        script_args: Optional[Union[list, str]] = None,
        env: Optional[Dict] = None,
        cloud_compute: Optional[CloudCompute] = None,
        script_path: Optional[str] = None,
        study: Optional[optuna.Study] = None,
        logger: str = "streamlit",
        project: Optional[str] = None,
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
        self.n_trials = n_trials
        self.simultaneous_trials = simultaneous_trials
        self.num_trials = simultaneous_trials
        self._study = study or optuna.create_study()
        self.logger = logger

        if logger == Loggers.STREAMLIT:
            self.hi_plot = HiPlotFlow()
        elif logger == Loggers.WANDB:
            self.hi_plot = None
            self.wandb_storage_id = None
            self._wandb_api = WandB()
            self._wandb_api.validate_auth()

        self.sweep_id = str(uuid.uuid4()).split("-")[0] if not project else project

        for trial_id in range(n_trials):
            objective_work = objective_cls(
                script_path=script_path or ".",
                env=env,
                script_args=script_args,
                cloud_compute=cloud_compute,
                parallel=True,
                cache_calls=True,
                logger=logger,
                trial_id=trial_id,
                sweep_id=self.sweep_id,
                **objective_work_kwargs,
            )
            setattr(self, f"w_{trial_id}", objective_work)

        self._trials = {}

    def run(self):
        if self.wandb_storage_id is None:
            self.wandb_storage_id = self._wandb_api.create_report(self.sweep_id)
        if self.num_trials > self.n_trials:
            return

        has_told_study = []

        for trial_idx in range(self.num_trials):
            work_objective = getattr(self, f"w_{trial_idx}")
            if work_objective.status.stage == WorkStageStatus.NOT_STARTED:
                distributions = work_objective.distributions()
                trial = self._study.ask(distributions)
                self._trials[trial_idx] = trial
                work_objective.run(params=trial.params)

            if work_objective.reports and not work_objective.pruned:
                trial = self._trials[work_objective.trial_id]
                for report in work_objective.reports:
                    if report not in work_objective.flow_reports:
                        trial.report(*report)
                        work_objective.flow_reports.append(report)
                    if trial.should_prune():
                        print(f"Trail {trial_idx} pruned.")
                        work_objective.pruned = True
                        work_objective.stop()
                        break

            if (
                work_objective.best_model_score
                and not work_objective.has_stopped
                and not work_objective.pruned
            ):
                # TODO: Understand why this is failing.
                try:
                    self._study.tell(
                        work_objective.trial_id, work_objective.best_model_score
                    )
                except RuntimeError:
                    pass
                if self.hi_plot:
                    self.hi_plot.data.append(
                        {"x": work_objective.best_model_score, **work_objective.params}
                    )
                work_objective.stop()
                print(
                    f"Trial {trial_idx} finished with value: {work_objective.best_model_score} and parameters: {work_objective.params}. "
                    f"Best is trial {self._study.best_trial.number} with value: {self._study.best_trial.value}."
                )

            has_told_study.append(work_objective.has_stopped)

        if all(has_told_study):
            self._wandb_api.update_report()
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
            content = [{"name": "Experiment", "content": content}]
        else:
            if self.wandb_storage_id is not None:
                reports = f"https://wandb.ai/{os.getenv('WANDB_ENTITY')}/{self.sweep_id}/reports/{self.sweep_id}"
                tab1 = {"name": "Project", "content": reports}
                sweep_report = f"https://wandb.ai/{os.getenv('WANDB_ENTITY')}/{self.sweep_id}/reports/{self.sweep_id}--{self.wandb_storage_id}"
                tab2 = {"name": "Report", "content": sweep_report}
                content = [tab1, tab2]
            else:
                reports = f"https://wandb.ai/{os.getenv('WANDB_ENTITY')}/{self.sweep_id}/reports/{self.sweep_id}"
                tab1 = {"name": "Project", "content": reports}
                content = [tab1]
        return content
