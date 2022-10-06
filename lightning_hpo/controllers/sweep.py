import urllib.parse
from typing import List

from lightning.app.storage import Drive
from lightning.app.structures import Dict

from lightning_hpo import Sweep
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
            self.tensorboard_sweep_id = [c.sweep_id for c in self.db.get(TensorboardConfig)]

        for tensorboard in self.db.get(TensorboardConfig):
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
                    self.db.post(TensorboardConfig(sweep_id=id, shared_folder=str(drive.drive_root)))
                elif sweep.stage in (Stage.FAILED, Stage.SUCCEEDED):
                    for tensorboard in self.db.get(TensorboardConfig):
                        if tensorboard.sweep_id == id:
                            tensorboard.desired_stage = Stage.STOPPED
                            self.db.put(tensorboard)

            if work_name not in self.r and sweep.stage != Stage.SUCCEEDED:
                self.r[work_name] = Sweep.from_config(
                    sweep,
                    code={"drive": self.drive, "name": id},
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
        if work_name not in self.r:
            self.db.post(config)
            return f"Launched a Sweep '{config.sweep_id}'."
        return f"The current Sweep '{config.sweep_id}' is running. It couldn't be updated."

    def show_sweeps(self) -> List[Dict]:
        if self.db_url:
            return [sweep.dict() for sweep in self.db.get()]
        return []

    def stop_sweep(self, config: StopSweepConfig):
        work_name = urllib.parse.quote_plus(config.sweep_id)
        if work_name in self.r:
            # TODO: Add support for __del__ in lightning
            sweep: Sweep = self.r[work_name]
            for w in sweep.works():
                w.stop()
            sweep.stage = Stage.STOPPED
            sweep_config = sweep.collect_model()
            for trial in sweep_config.trials.values():
                if trial.stage == Stage.RUNNING:
                    trial.stage = Stage.STOPPED
            self.db.put(sweep_config)
            return f"Stopped the sweep `{config.sweep_id}`"
        return f"We didn't find the sweep `{config.sweep_id}`"

    def delete_sweep(self, config: DeleteSweepConfig):
        work_name = urllib.parse.quote_plus(config.sweep_id)
        if work_name in self.r:
            sweep: Sweep = self.r[work_name]
            for w in sweep.works():
                w.stop()
            self.db.delete(sweep.collect_model())
            del self.r[work_name]
            return f"Deleted the sweep `{config.sweep_id}`"
        return f"We didn't find the sweep `{config.sweep_id}`"

    def stop_experiment(self, config: StopExperimentConfig):
        sweeps_config: List[SweepConfig] = self.db.get()
        for sweep in sweeps_config:
            for trial_id, trial in enumerate(sweep.trials.values()):
                if config.name == trial.name:
                    if trial.stage == Stage.SUCCEEDED:
                        return f"The current trial `{trial.name}` has already succeeded."
                    self.r[sweep.sweep_id].stop_experiment(trial_id)
                    return f"The current trial `{trial.name}` has been stopped."
        return f"The current trial `{config.name}` doesn't exist."

    def configure_commands(self):
        return [
            {"delete sweep": DeleteSweepCommand(self.delete_sweep)},
            {"run sweep": RunSweepCommand(self.run_sweep)},
            {"show sweeps": ShowSweepsCommand(self.show_sweeps)},
            {"stop sweep": StopSweepCommand(self.stop_sweep)},
            {"stop experiment": StopExperimentCommand(self.stop_experiment)},
        ]
