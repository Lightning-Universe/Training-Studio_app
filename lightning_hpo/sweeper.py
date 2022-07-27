from lightning import LightningFlow, CloudCompute, BuildConfig
from lightning_hpo import Optimizer
from lightning_hpo.commands.sweep import SweepCommand, SweepConfig
from lightning.app.storage import Drive
from lightning_hpo.file_server import FileServer
from lightning.app.storage.path import Path
from lightning.app.structures import Dict
from lightning_hpo.utils import get_best_model_path, config_to_distributions
from typing import Optional

class HPOSweeper(LightningFlow):

    def __init__(self):
        super().__init__()
        self.sweeps = Dict()
        self.drive = Drive("lit://code")
        self.file_server = FileServer(self.drive)

    def run(self):
        self.file_server.run()
        if self.file_server.alive():
            for sweep in self.sweeps.values():
                sweep.run()

    def create_sweep(self, config: SweepConfig) -> str:
        sweep_ids = list(self.sweeps.keys())
        if config.sweep_id not in sweep_ids:
            self.sweeps[config.sweep_id] = Optimizer(
                script_path=config.script_path,
                n_trials=config.n_trials,
                simultaneous_trials=config.simultaneous_trials,
                framework=config.framework,
                script_args=config.script_args,
                distributions=config_to_distributions(config),
                cloud_compute=CloudCompute(config.cloud_compute),
                sweep_id=config.sweep_id,
                code={"drive": self.drive, "name": config.sweep_id},
                num_nodes=config.num_nodes,
                cloud_build_config=BuildConfig(requirements=config.requirements),
                raise_exception=False,
            )
            return f"Launched a sweep {config.sweep_id}"
        elif self.sweeps[config.sweep_id].has_failed:
            self.sweeps[config.sweep_id].restart_count += 1
            self.sweeps[config.sweep_id].has_failed = False
            return f"Updated code for Sweep {config.sweep_id}."
        else:
            return f"The current Sweep {config.sweep_id} is running. It couldn't be updated."

    def configure_commands(self):
        return [{"sweep": SweepCommand(self.create_sweep)}]

    def configure_layout(self):
        tabs = []
        for sweep in self.sweeps.values():
            tabs = tabs + sweep.configure_layout()
        return tabs

    @property
    def best_model_score(self) -> Optional[Path]:
        return get_best_model_path(self)