from lightning import LightningFlow, CloudCompute
import optuna
from lightning.structures import Dict
from lightning_hpo.objective import BaseObjectiveWork
from lightning_hpo.hyperplot import HiPlotFlow
from typing import Optional, Union, Dict, Type, Any
from lightning.storage.path import Path
from lightning.utilities.enum import WorkStageStatus
from optuna.trial import TrialState
from lightning import structures

class OptunaPythonScript(LightningFlow):
    def __init__(
        self,
        script_path: str,
        total_trials: int,
        simultaneous_trials: int,
        objective_work_cls: Type[BaseObjectiveWork],
        study: Optional[optuna.study.Study] = None,
        script_args: Optional[Union[list, str]] = None,
        env: Optional[Dict] = None,
        cloud_compute: Optional[CloudCompute] = None,
        **objective_work_kwargs: Any,

    ):
        """The OptunaPythonScript class enables to easily run a Python Script with Lightning
        :class:`~lightning.utilities.tracer.Tracer` with state-of-the-art distributed.

        Arguments:
            script_path: Path of the python script to run.
            total_trials: Number of HPO trials to run.
            simultaneous_trials: Number of parallel trials to run.
            objective_work_cls: Your custom base objective work.
            study: Optional Optuna study to collect the parameters.
            script_args: Optional script arguments.
            env: Environment variables to be passed to the script.
            cloud_compute: The cloud compute on which the Work should run on.
            parallel: Whether the Work should be async from the flow perspective.
            objective_work_kwargs: Your custom keywords arguments passed to your custom objective work class.
        """
        super().__init__()
        self.total_trials = total_trials
        self.simultaneous_trials = simultaneous_trials
        self._study = study or optuna.create_study()
        self.workers = Dict()

        for trial_id in range(self.total_trials):
            self.workers[f"w_{trial_id}"] = objective_work_cls(
                parallel=True,
                script_path=script_path,
                script_args=script_args,
                env=env,
                cloud_compute=cloud_compute,
                **objective_work_kwargs,
            )

        self.hi_plot = HiPlotFlow()

    def run(self):
        for trial_id in range(self.total_trials):
            worker = self.workers[f"w_{trial_id}"]
            if not worker.has_started:
                params = self._study.ask(worker.distributions())
                worker.run(trial_id=trial_id, params=params)

            if worker.has_succeeded:
                self.hi_plot.data.append({"x": worker.best_model_score, **worker.params})
                self._study.tell(trial_id, -1 * worker.best_model_score)
                worker.stop()

    @property
    def best_model_score(self) -> Optional[float]:
        """TO BE IMPLEMENTED"""

    @property
    def best_model_path(self) -> Optional[Path]:
        """TO BE IMPLEMENTED"""