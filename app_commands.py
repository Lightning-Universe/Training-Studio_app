from lightning import LightningFlow, LightningApp
from lightning_hpo import Optimizer
from lightning_hpo.commands.sweep import SweepCommand, SweepConfig
from lightning.app.storage import Drive
from lightning_hpo.file_server import FileServer
from lightning.app.storage.path import Path
from lightning.app.structures import Dict
from lightning_hpo.utils import get_best_model_path
from typing import Optional
from optuna.distributions import CategoricalDistribution, LogUniformDistribution, UniformDistribution
from lightning.app import BuildConfig

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
        # TODO: Resolve this bug, we shouldn't need to use list
        sweep_ids = list(self.sweeps.keys())
        if config.sweep_id not in sweep_ids:
            distributions = {}
            mapping_name_to_cls = {
                "categorical": CategoricalDistribution,
                "uniform": UniformDistribution,
                "log_uniform": LogUniformDistribution,
            }
            for k, v in config.distributions.items():
                dist_cls = mapping_name_to_cls[v.pop("distribution")]
                distributions[k] = dist_cls(**v)

            self.sweeps[config.sweep_id] = Optimizer(
                script_path=config.script_path,
                n_trials=config.n_trials,
                simultaneous_trials=config.simultaneous_trials,
                framework=config.framework,
                script_args=config.script_args,
                distributions=distributions,
                cloud_compute=config.cloud_compute,
                drive=self.drive,
                sweep_id=config.sweep_id,
                code=config.code,
                cloud_build_config=BuildConfig(requirements=config.requirements)
            )
            return f"Launched a sweep {config.sweep_id}"
        else:
            # TODO: Understand how to abstract this from the framework.
            works = self.sweeps[config.sweep_id].works()
            if any(w.status.stage == "failed" for w in works):
                for w in works:
                    if w.status.stage == "failed":
                        w.restart_count += 1
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

app = LightningApp(HPOSweeper())