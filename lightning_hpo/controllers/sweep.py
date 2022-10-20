import urllib.parse
from typing import List

from lightning.app.storage import Drive
from lightning.app.structures import Dict

from lightning_hpo import Sweep
from lightning_hpo.commands.drive.create import DriveConfig
from lightning_hpo.commands.experiment.delete import DeleteExperimentCommand, DeleteExperimentConfig
from lightning_hpo.commands.experiment.run import RunExperimentCommand
from lightning_hpo.commands.experiment.show import ShowExperimentsCommand
from lightning_hpo.commands.experiment.stop import StopExperimentCommand, StopExperimentConfig
from lightning_hpo.commands.sweep.delete import DeleteSweepCommand, DeleteSweepConfig
from lightning_hpo.commands.sweep.run import RunSweepCommand, SweepConfig
from lightning_hpo.commands.sweep.show import ShowSweepsCommand
from lightning_hpo.commands.sweep.stop import StopSweepCommand, StopSweepConfig
from lightning_hpo.commands.tensorboard.stop import TensorboardConfig
from lightning_hpo.controllers.controller import Controller
from lightning_hpo.utilities.enum import Stage


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
                            tensorboard.desired_stage = Stage.STOPPED
                            self.db.update(tensorboard)

            if work_name not in self.r and sweep.stage != Stage.SUCCEEDED:
                drives: List[DriveConfig] = self.db.select_all(DriveConfig)
                self.r[work_name] = Sweep.from_config(
                    sweep,
                    code={"drive": self.drive, "name": id},
                    drives=[
                        Drive(drive.source, root_folder=drive.mount_path)
                        for drive in drives
                        if drive.name in sweep.drive_names
                    ],
                )

    def on_reconcile_end(self, updates: List[SweepConfig]):
        for update in updates:
            if update.stage == Stage.SUCCEEDED:
                work_name = urllib.parse.quote_plus(update.sweep_id)
                for w in self.r[work_name].works():
                    w.stop()
                self.r.pop(work_name)

    def run_sweep(self, config: SweepConfig) -> str:
        work_name = urllib.parse.quote_plus(config.sweep_id)
        drive_names = [drive.name for drive in self.db.select_all(DriveConfig)]

        for drive in config.drive_names:
            if drive not in drive_names:
                return f"The provided drive '{drive}' doesn't exists."

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
                return f"Deleted the sweep `{config.name}`"
        return f"We didn't find the sweep `{config.name}`"

    def delete_experiment(self, config: DeleteExperimentConfig):
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
