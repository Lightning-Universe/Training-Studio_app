import os
import uuid
from typing import Any, Dict, List, Optional, Tuple, Type, Union
from uuid import uuid4

from lightning import BuildConfig, CloudCompute, LightningFlow
from lightning.app.components.python.tracer import Code
from lightning.app.frontend import StaticWebFrontend
from lightning.app.storage.mount import Mount
from lightning.app.storage.path import Path
from lightning.app.utilities.app_helpers import _LightningAppRef
from lightning_utilities.core.apply_func import apply_to_collection

from lightning_training_studio.algorithm.base import Algorithm
from lightning_training_studio.algorithm.optuna import GridSearch, OptunaAlgorithm, RandomSearch
from lightning_training_studio.commands.sweep.run import ExperimentConfig, SweepConfig
from lightning_training_studio.commands.sweep.show import ShowSweepsCommand
from lightning_training_studio.controllers.controller import ControllerResource
from lightning_training_studio.distributions.distributions import Distribution
from lightning_training_studio.framework.agnostic import Objective
from lightning_training_studio.loggers import LoggerType
from lightning_training_studio.utilities.enum import Stage
from lightning_training_studio.utilities.utils import (
    _check_stage,
    _resolve_objective_cls,
    get_best_model_path,
    get_best_model_score,
    HPOCloudCompute,
)


class CustomBuildConfig(BuildConfig):
    def __init__(self, *args, packages, **kwargs):
        super().__init__(*args, **kwargs)
        self.packages = packages

    def build_commands(self):
        package_installs = [f"sudo apt install {package}" for package in self.packages]
        return super().build_commands() + ["sudo apt update"] + package_installs


class Sweep(LightningFlow, ControllerResource):

    model = SweepConfig

    def __init__(
        self,
        total_experiments: int,
        objective_cls: Optional[Type[Objective]] = None,
        parallel_experiments: int = 1,
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
        total_experiments_done: Optional[int] = 0,
        requirements: Optional[List[str]] = None,
        packages: Optional[List[str]] = None,
        experiments: Optional[Dict[int, Dict]] = None,
        stage: Optional[str] = Stage.NOT_STARTED,
        logger_url: str = "",
        pip_install_source: bool = False,
        data: Optional[List[Tuple[str, str]]] = None,
        **objective_kwargs: Any,
    ):
        """The Sweep class enables to easily run a Python Script with Lightning
        :class:`~lightning.utilities.tracer.Tracer` with state-of-the-art distributed.
        Arguments:
            total_experiments: Number of HPO experiments to run.
            objective_cls: Your custom base objective work.
            parallel_experiments: Number of parallel experiments to run.
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
        self.total_experiments = total_experiments
        self.parallel_experiments = parallel_experiments
        self.total_experiments_done = total_experiments_done or 0
        self.requirements = requirements or []
        self.packages = packages or []
        self.script_args = script_args
        self.distributions = distributions or {}
        self.framework = framework
        self.cloud_compute = getattr(cloud_compute, "name", "default")
        self.num_nodes = getattr(cloud_compute, "count", 1) if cloud_compute else 1
        self.disk_size = getattr(cloud_compute, "disk_size", 1) if cloud_compute else 10
        self.logger = logger
        self.direction = direction
        self.experiments = experiments or {}
        self.stage = stage
        self.logger_url = logger_url
        self.pip_install_source = pip_install_source
        self.data = data

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
            "cloud_build_config": CustomBuildConfig(requirements=self.requirements, packages=self.packages),
            **objective_kwargs,
        }
        self._algorithm.register_distributions(self.distributions)
        self._algorithm.register_experiments(
            [t for t in experiments.values() if t["stage"] == Stage.SUCCEEDED] if experiments else []
        )
        self.restart_count = 0

    def run(self):
        if self.stage in (Stage.SUCCEEDED, Stage.STOPPED):
            return

        if self.total_experiments_done == self.total_experiments:
            self.stage = Stage.SUCCEEDED
            return

        for experiment_id in range(self.num_experiments):

            objective = self._get_objective(experiment_id)

            if objective:

                if _check_stage(objective, Stage.NOT_STARTED):
                    self._algorithm.experiment_start(experiment_id)
                    self._logger.on_after_experiment_start(self.sweep_id)

                if not self.experiments[experiment_id]["params"]:
                    self.stage = Stage.RUNNING
                    self.experiments[experiment_id]["params"] = self._algorithm.get_params(experiment_id)

                logger_url = self._logger.get_url(experiment_id)
                if logger_url is not None and self.logger_url != logger_url:
                    self.logger_url = logger_url

                if _check_stage(objective, Stage.FAILED):
                    continue

                objective.run(
                    params=self._algorithm.get_params(experiment_id),
                    restart_count=self.restart_count,
                )

                self.experiments[experiment_id]["progress"] = objective.progress
                self.experiments[experiment_id]["total_parameters"] = getattr(objective, "total_parameters", None)
                self.experiments[experiment_id]["start_time"] = getattr(objective, "start_time", None)
                self.experiments[experiment_id]["end_time"] = getattr(objective, "end_time", None)
                self.experiments[experiment_id]["best_model_score"] = getattr(objective, "best_model_score", None)
                self.experiments[experiment_id]["last_model_path"] = str(getattr(objective, "last_model_path", ""))

                if _check_stage(objective, Stage.FAILED):
                    self.experiments[experiment_id]["stage"] = Stage.FAILED
                    self.experiments[experiment_id]["exception"] = objective.status.message
                    objective.stop()

                if objective.reports and not self.experiments[experiment_id]["stage"] == "pruned":
                    if self._algorithm.should_prune(experiment_id, objective.reports):
                        self.experiments[experiment_id]["stage"] = Stage.PRUNED
                        objective.stop()
                        self.total_experiments_done += 1
                        continue

                if self.stage != Stage.FAILED and self.experiments[experiment_id]["stage"] == Stage.PENDING:
                    if self.experiments[experiment_id]["stage"] != objective.status:
                        self.stage = Stage.RUNNING
                        self.experiments[experiment_id]["stage"] = Stage.RUNNING

                if objective.best_model_score:
                    if self.experiments[experiment_id]["stage"] == Stage.SUCCEEDED:
                        pass
                    elif self.experiments[experiment_id]["stage"] not in (Stage.PRUNED, Stage.STOPPED, Stage.FAILED):
                        self._algorithm.experiment_end(experiment_id, objective.best_model_score)
                        self._logger.on_after_experiment_end(
                            sweep_id=self.sweep_id,
                            experiment_id=objective.experiment_id,
                            monitor=objective.monitor,
                            score=objective.best_model_score,
                            params=self._algorithm.get_params(experiment_id),
                        )
                        self.experiments[experiment_id]["best_model_score"] = objective.best_model_score
                        self.experiments[experiment_id]["best_model_path"] = str(objective.best_model_path)
                        self.experiments[experiment_id]["monitor"] = objective.monitor
                        self.experiments[experiment_id]["stage"] = Stage.SUCCEEDED
                        self.total_experiments_done += 1
                        objective.stop()

        if all(
            self.experiments[experiment_id]["stage"] == Stage.FAILED for experiment_id in range(self.num_experiments)
        ):
            self.stage = Stage.FAILED

    @property
    def num_experiments(self) -> int:
        return min(self.total_experiments_done + self.parallel_experiments, self.total_experiments)

    @property
    def best_model_score(self) -> Optional[float]:
        return get_best_model_score(self)

    @property
    def best_model_path(self) -> Optional[Path]:
        return get_best_model_path(self)

    def stop_experiment(self, experiment_id: int):
        objective = self._get_objective(experiment_id)
        if objective:
            objective.stop()
            self.experiments[experiment_id]["stage"] = Stage.STOPPED
            self.total_experiments_done += 1

    def _get_objective(self, experiment_id: int):
        experiment_config = self.experiments.get(experiment_id, None)
        if experiment_config is None:
            experiment_config = ExperimentConfig(
                name=str(uuid4()).split("-")[-1][:7],
                best_model_score=None,
                monitor=None,
                best_model_path=None,
                stage=Stage.PENDING,
                params={},
            ).dict()
            self.experiments[experiment_id] = experiment_config

        if experiment_config["stage"] == Stage.SUCCEEDED:
            return

        objective = getattr(self, f"w_{experiment_id}", None)
        if objective is None:
            cloud_compute = CloudCompute(
                name=self.cloud_compute if self.cloud_compute else "cpu",
                disk_size=self.disk_size,
                mounts=[Mount(source, mount_path) for source, mount_path in self.data] if self.data else None,
            )
            objective = self._objective_cls(
                experiment_id=experiment_id,
                experiment_name=experiment_config["name"],
                cloud_compute=cloud_compute,
                last_model_path=experiment_config["last_model_path"],
                pip_install_source=self.pip_install_source,
                **self._kwargs,
            )
            setattr(self, f"w_{experiment_id}", objective)
            self.experiments[experiment_id]["stage"] = Stage.PENDING
        return objective

    @classmethod
    def from_config(
        cls, config: SweepConfig, code: Optional[Code] = None, data: Optional[List[Tuple[str, str]]] = None
    ):

        if config.algorithm == "grid_search":
            algorithm = GridSearch({k: v.dict()["params"]["choices"] for k, v in config.distributions.items()})
            config.total_experiments = algorithm.total_experiments
            config.parallel_experiments = algorithm.total_experiments

        elif config.algorithm == "random_search":
            algorithm = RandomSearch({k: v.dict() for k, v in config.distributions.items()})
        else:
            algorithm = OptunaAlgorithm(direction=config.direction)

        return cls(
            script_path=config.script_path,
            total_experiments=config.total_experiments,
            parallel_experiments=config.parallel_experiments,
            framework=config.framework,
            script_args=config.script_args,
            total_experiments_done=config.total_experiments_done,
            distributions={k: v.dict() for k, v in config.distributions.items()},
            cloud_compute=HPOCloudCompute(
                config.cloud_compute,
                count=config.num_nodes,
                disk_size=config.disk_size,
            ),
            sweep_id=config.sweep_id,
            code=code,
            logger=config.logger,
            algorithm=algorithm,
            experiments={k: v.dict() for k, v in config.experiments.items()},
            direction=config.direction,
            stage=config.stage,
            logger_url=config.logger_url,
            data=data,
            pip_install_source=config.pip_install_source,
            requirements=config.requirements,
            packages=config.packages,
        )

    def configure_layout(self):
        app = _LightningAppRef().get_current()
        if app and app.root == self:
            return StaticWebFrontend(os.path.join(os.path.dirname(os.path.dirname(__file__)), "app", "ui", "build"))
        return self._logger.configure_layout()

    def show_sweeps(self):
        return [self.collect_model()]

    def show_tensorboards(self):
        return []

    def configure_commands(self):
        return [
            {"show sweeps": ShowSweepsCommand(self.show_sweeps)},
            {"show tensorboards": self.show_tensorboards},
        ]
