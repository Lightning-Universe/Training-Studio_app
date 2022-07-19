from lightning import LightningFlow, LightningApp, CloudCompute
from lightning_hpo import Optimizer
from lightning_hpo.commands.sweep import SweepCommand, SweepConfig
from lightning.app.storage.path import Path
from lightning.app.structures import Dict
from lightning_hpo.utils import get_best_model_path
from typing import Optional

class HPOSweeper(LightningFlow):

    def __init__(self):
        super().__init__()
        self.sweeps = Dict()

    def run(self):
        for sweep in self.sweeps.values():
            sweep.run()

    def create_sweep(self, config: SweepConfig) -> None:
        if config.sweep_id not in self.sweeps:
            self.sweeps[config.sweep_id] = Optimizer(
                script_path=config.script_path,
                n_trials=config.n_trials,
                simultaneous_trials=config.simultaneous_trials,
                framework=config.framework,
                script_args=config.script_args,
                distributions=config.distributions,
                cloud_compute=config.cloud_compute,
            )

    def configure_commands(self):
        return [{"sweep": SweepCommand(self.create_sweep)}]

    def configure_layout(self):
        return [sweep.configure_layout() for sweep in self.sweeps.values()]

    @property
    def best_model_score(self) -> Optional[Path]:
        return get_best_model_path(self)

app = LightningApp(HPOSweeper())