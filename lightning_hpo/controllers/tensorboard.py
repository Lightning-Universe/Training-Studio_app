from typing import List

from lightning.app.storage import Drive

from lightning_hpo.commands.tensorboard.stop import TensorboardConfig
from lightning_hpo.components.tensorboard import Tensorboard
from lightning_hpo.controllers.controller import Controller
from lightning_hpo.utilities.enum import Status


class TensorboardController(Controller):

    model = TensorboardConfig

    def on_reconcile_start(self, configs: List[TensorboardConfig]):
        for config in configs:
            if config.sweep_id not in self.r:
                if config.status != Status.RUNNING and config.desired_state == Status.RUNNING:
                    self.r[config.sweep_id] = Tensorboard(
                        drive=Drive(f"lit://{config.sweep_id}"),
                        config=config,
                    )

    def show_tensorboards(self) -> List[TensorboardConfig]:
        if self.db_url:
            return self.db.get()
        return []

    def configure_commands(self):
        return [{"show tensorboards": self.show_tensorboards}]
