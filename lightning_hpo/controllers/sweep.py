from typing import List

from lightning.app.storage import Drive
from lightning.app.structures import Dict

from lightning_hpo import Sweep
from lightning_hpo.commands.sweep.delete import DeleteSweepCommand, DeleteSweepConfig
from lightning_hpo.commands.sweep.run import RunSweepCommand, SweepConfig
from lightning_hpo.commands.sweep.show import ShowSweepsCommand
from lightning_hpo.commands.sweep.stop import StopSweepCommand, StopSweepConfig
from lightning_hpo.commands.tensorboard.stop import TensorboardConfig
from lightning_hpo.controllers.controller import Controller
from lightning_hpo.loggers import LoggerType
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
            if tensorboard.sweep_id in self.r:
                self.r[tensorboard.sweep_id].logger_url = tensorboard.url

        # 2: Create the Sweeps
        for sweep in sweeps:
            id = sweep.sweep_id
            if sweep.logger == LoggerType.TENSORBOARD.value and id not in self.tensorboard_sweep_id:
                self.tensorboard_sweep_id.append(id)
                drive = Drive(f"lit://{id}")
                self.db.post(TensorboardConfig(sweep_id=id, shared_folder=str(drive.drive_root)))

            if id not in self.r and sweep.stage != Stage.SUCCEEDED:
                self.r[id] = Sweep.from_config(
                    sweep,
                    code={"drive": self.drive, "name": id},
                )

    def on_reconcile_end(self, updates: List[SweepConfig]):
        for update in updates:
            if update.stage == Stage.SUCCEEDED:
                for w in self.r[update.sweep_id].works():
                    w.stop()
                self.r.pop(update.sweep_id)

    def run_sweep(self, config: SweepConfig) -> str:
        sweep_ids = list(self.r.keys())
        if config.sweep_id not in sweep_ids:
            self.db.post(config)
            return f"Launched a sweep {config.sweep_id}"
        return f"The current Sweep {config.sweep_id} is running. It couldn't be updated."

    def show_sweeps(self) -> List[Dict]:
        if self.db_url:
            return [sweep.dict() for sweep in self.db.get()]
        return []

    def stop_sweep(self, config: StopSweepConfig):
        sweep_ids = list(self.r.keys())
        if config.sweep_id in sweep_ids:
            # TODO: Add support for __del__ in lightning
            sweep: Sweep = self.r[config.sweep_id]
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
        sweep_ids = list(self.r.keys())
        if config.sweep_id in sweep_ids:
            sweep: Sweep = self.r[config.sweep_id]
            for w in sweep.works():
                w.stop()
            self.db.delete(sweep.collect_model())
            del self.r[config.sweep_id]
            return f"Deleted the sweep `{config.sweep_id}`"
        return f"We didn't find the sweep `{config.sweep_id}`"

    def configure_commands(self):
        return [
            {"delete sweep": DeleteSweepCommand(self.delete_sweep)},
            {"run sweep": RunSweepCommand(self.run_sweep)},
            {"show sweeps": ShowSweepsCommand(self.show_sweeps)},
            {"stop sweep": StopSweepCommand(self.stop_sweep)},
        ]
