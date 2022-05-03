from lightning import LightningFlow, CloudCompute
import optuna
from lightning_hpo.objective import AbstractObjectiveWork
from lightning_hpo.hyperplot import HiPlotFlow
from typing import Optional, Union, Dict, Type, Any
from lightning.storage.path import Path
from lightning.utilities.enum import WorkStageStatus

class OptunaPythonScript(LightningFlow):
    def __init__(
        self,
        script_path: str,
        total_trials,
        simultaneous_trials,
        objective_work_cls: Type[AbstractObjectiveWork],
        objective_work_kwargs: Optional[Dict[str, Any]] = None,
        study: Optional[optuna.study.Study] = None,
        script_args: Optional[Union[list, str]] = None,
        env: Optional[Dict] = None,
        cloud_compute: Optional[CloudCompute] = None

    ):
        """The OptunaPythonScript class enables to easily run a Python Script with Lightning
        :class:`~lightning.utilities.tracer.Tracer` with state-of-the-art distributed.

        Arguments:
            script_path: Path of the python script to run.
            script_path: The arguments to be passed to the script.
            env: Environment variables to be passed to the script.
            cloud_compute: The cloud compute on which the Work should run on.
            blocking: Whether the Work should be blocking or asynchornous.
            run_once: Whether the Work should run_once.
            exposed_ports: Dictionary of ports exposed by this specific work.
            raise_exception: Whether to raise any expection from the script_path execution.
        """
        super().__init__()
        self.total_trials = total_trials
        self.simultaneous_trials = simultaneous_trials
        self.num_trials = simultaneous_trials
        self._study = study or optuna.create_study()
        for trial_idx in range(total_trials):
            objective_work = objective_work_cls(
                script_path=script_path,
                env=env,
                script_args=script_args,
                cloud_compute=cloud_compute,
                blocking=False,
                run_once=True,
                **(objective_work_kwargs or {}),
            )
            setattr(self, f"w_{trial_idx}", objective_work)

        self.hi_plot = HiPlotFlow()

    def run(self):
        if self.num_trials > self.total_trials:
            return

        has_told_study = []

        for trial_idx in range(self.num_trials):
            work_objective = getattr(self, f"w_{trial_idx}")
            if work_objective.status.stage == WorkStageStatus.NOT_STARTED:
                trial = self._study.ask(work_objective.distributions())
                print(f"Starting work {trial_idx} with the following parameters {trial.params}")
                work_objective.run(trial_id=trial._trial_id, **trial.params)

            if work_objective.best_model_score and not work_objective.has_told_study:
                self._study.tell(work_objective.trial_id, work_objective.best_model_score)
                self.hi_plot.data.append({"x": -1 * work_objective.best_model_score, **work_objective.params})
                work_objective.has_told_study = True

            has_told_study.append(work_objective.has_told_study)

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