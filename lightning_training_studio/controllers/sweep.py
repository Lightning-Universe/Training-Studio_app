import urllib.parse
from typing import List

from lightning.app.storage import Drive
from lightning.app.structures import Dict

from lightning_training_studio import Sweep
from lightning_training_studio.commands.data.create import DataConfig
from lightning_training_studio.commands.experiment.delete import DeleteExperimentCommand, DeleteExperimentConfig
from lightning_training_studio.commands.experiment.run import RunExperimentCommand
from lightning_training_studio.commands.experiment.show import ShowExperimentsCommand
from lightning_training_studio.commands.experiment.stop import StopExperimentCommand, StopExperimentConfig
from lightning_training_studio.commands.logs.show import ShowLogsConfig
from lightning_training_studio.commands.sweep.delete import DeleteSweepCommand, DeleteSweepConfig
from lightning_training_studio.commands.sweep.run import RunSweepCommand, SweepConfig
from lightning_training_studio.commands.sweep.show import ShowSweepsCommand
from lightning_training_studio.commands.sweep.stop import StopSweepCommand, StopSweepConfig
from lightning_training_studio.commands.tensorboard.stop import TensorboardConfig
from lightning_training_studio.controllers.controller import Controller
from lightning_training_studio.utilities.enum import Stage


class SweepController(Controller):

    model = SweepConfig

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tensorboard_sweep_id = None

    def on_reconcile_start(self, sweeps: List[SweepConfig]):
        # 1: Retrieve the tensorboard configs from the database
        if self.tensorboard_sweep_id is None:
            self.tensorboard_sweep_id = [c.sweep_id for c in self.db.select_all(TensorboardConfig)]

        for tensorboard in self.db.select_all(TensorboardConfig):
            work_name = urllib.parse.quote_plus(tensorboard.sweep_id)
            if work_name in self.r:
                self.r[work_name].logger_url = tensorboard.url

        # 2: Create the Sweeps
        for sweep in sweeps:
            id = sweep.sweep_id
            work_name = urllib.parse.quote_plus(id)
            if sweep.is_tensorboard():
                drive = Drive(f"lit://{id}")
                if id not in self.tensorboard_sweep_id:
                    self.tensorboard_sweep_id.append(id)
                    self.db.insert(TensorboardConfig(sweep_id=id, shared_folder=str(drive.drive_root)))
                elif sweep.stage in (Stage.FAILED, Stage.SUCCEEDED):
                    for tensorboard in self.db.select_all(TensorboardConfig):
                        if tensorboard.sweep_id == id:
                            tensorboard.desired_stage = Stage.DELETED
                            self.db.update(tensorboard)

            if work_name not in self.r and sweep.stage != Stage.SUCCEEDED:
                all_data: List[DataConfig] = self.db.select_all(DataConfig)
                self.r[work_name] = Sweep.from_config(
                    sweep,
                    code={"drive": self.drive, "name": id},
                    data=[
                        (data.source, sweep.data[data.name] or data.mount_path)
                        for data in all_data
                        if data.name in sweep.data
                    ],
                )

    def on_reconcile_end(self, updates: List[SweepConfig]):
        for update in updates:
            if update.stage == Stage.SUCCEEDED:
                work_name = urllib.parse.quote_plus(update.sweep_id)
                for w in self.r[work_name].works():
                    w.stop()

    def run_sweep(self, config: SweepConfig) -> str:
        work_name = urllib.parse.quote_plus(config.sweep_id)
        data_names = [data.name for data in self.db.select_all(DataConfig)]

        for data in config.data:
            if data not in data_names:
                return f"The provided Data '{data}' doesn't exist."

        if work_name not in self.r:
            self.db.insert(config)
            return f"Launched a Sweep '{config.sweep_id}'."
        return f"The current Sweep '{config.sweep_id}' is running. It couldn't be updated."

    def show_sweeps(self) -> List[Dict]:
        if self.db_url:
            return [sweep.dict() for sweep in self.db.select_all()]
        return []

    def stop_sweep(self, config: StopSweepConfig):
        work_name = urllib.parse.quote_plus(config.sweep_id)
        if work_name in self.r:
            # TODO: Add support for __del__ in lightning
            sweep: Sweep = self.r[work_name]
            for w in sweep.works():
                w.stop()
            sweep.stage = Stage.STOPPED
            sweep_config: SweepConfig = sweep.collect_model()
            for experiment in sweep_config.experiments.values():
                if experiment.stage == Stage.RUNNING:
                    experiment.stage = Stage.STOPPED
            self.db.update(sweep_config)
            return f"Stopped the sweep `{config.sweep_id}`"
        return f"We didn't find the sweep `{config.sweep_id}`"

    def delete_sweep(self, config: DeleteSweepConfig):
        sweeps: List[SweepConfig] = self.db.select_all()
        for sweep in sweeps:
            if config.name != sweep.sweep_id:
                continue
            else:
                if config.name in self.r:
                    sweep: Sweep = self.r[config.name]
                    for w in sweep.works():
                        w.stop()
                    sweep = sweep.collect_model()
                    del self.r[config.name]
                self.db.delete(sweep)
                for tensorboard in self.db.select_all(TensorboardConfig):
                    if tensorboard.sweep_id == config.name:
                        tensorboard.desired_stage = Stage.DELETED
                        self.db.update(tensorboard)
                return f"Deleted the sweep `{config.name}`"
        return f"We didn't find the sweep `{config.name}`"

    def delete_experiment(self, config: DeleteExperimentConfig):
        sweeps: List[SweepConfig] = self.db.select_all()
        for sweep in sweeps:
            for experiment in sweep.experiments.values():
                if config.name == experiment.name:
                    if config.name != sweep.sweep_id:
                        return f"The experiment `{config.name}` is part of sweep `{sweep.sweep_id}`, which includes multiple experiments. Deleting individual experiments of a sweep is currently unsupported."
                    if config.name in self.r:
                        sweep: Sweep = self.r[config.name]
                        for w in sweep.works():
                            w.stop()
                        sweep = sweep.collect_model()
                        del self.r[config.name]
                    self.db.delete(sweep)
                    for tensorboard in self.db.select_all(TensorboardConfig):
                        if tensorboard.sweep_id == config.name:
                            tensorboard.desired_stage = Stage.DELETED
                            self.db.update(tensorboard)
                    return f"Deleted the experiment `{config.name}`"
        return f"We didn't find the experiment `{config.name}`"

    def run_experiment(self, config: SweepConfig) -> str:
        work_name = urllib.parse.quote_plus(config.sweep_id)
        if work_name not in self.r:
            self.db.insert(config)
            return f"Launched an experiment '{config.sweep_id}'."
        return f"The experiment '{config.sweep_id}' is running. It can't be updated."

    def stop_experiment(self, config: StopExperimentConfig):
        sweeps_config: List[SweepConfig] = self.db.select_all()
        for sweep in sweeps_config:
            for experiment_id, experiment in enumerate(sweep.experiments.values()):
                if config.name == experiment.name:
                    if experiment.stage == Stage.SUCCEEDED:
                        return f"The current experiment `{experiment.name}` has already succeeded."
                    self.r[sweep.sweep_id].stop_experiment(experiment_id)
                    return f"The current experiment `{experiment.name}` has been stopped."
        return f"The current experiment `{config.name}` doesn't exist."

    def show_logs(self) -> List[ShowLogsConfig]:
        data = []
        for sweep in self.db.select_all():
            if sweep.sweep_id in self.r:
                works = self.r[sweep.sweep_id].works()
                if sweep.algorithm:
                    data.append(ShowLogsConfig(name=sweep.sweep_id, components=[w.name for w in works]))
                for experiment in sweep.experiments.values():
                    data.append(
                        ShowLogsConfig(
                            name=experiment.name,
                            components=[w.name for w in works if w.experiment_name == experiment.name],
                        )
                    )
        return data

    def configure_commands(self):
        return [
            {"delete sweep": DeleteSweepCommand(self.delete_sweep)},
            {"run sweep": RunSweepCommand(self.run_sweep)},
            {"show sweeps": ShowSweepsCommand(self.show_sweeps)},
            {"stop sweep": StopSweepCommand(self.stop_sweep)},
            {"run experiment": RunExperimentCommand(self.run_experiment)},
            {"stop experiment": StopExperimentCommand(self.stop_experiment)},
            {"show experiments": ShowExperimentsCommand(self.show_sweeps)},
            {"delete experiment": DeleteExperimentCommand(self.delete_experiment)},
        ]
