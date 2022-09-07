from typing import List

from lightning.app.storage import Drive

from lightning_hpo.commands.tensorboard.stop import TensorboardConfig
from lightning_hpo.components.tensorboard import Tensorboard
from lightning_hpo.controllers.controller import Controller


class TensorboardController(Controller):

    model = TensorboardConfig

    def on_reconcile_start(self, configs: List[TensorboardConfig]):
        for config in configs:
            if config.sweep_id not in self.r:
                self.r[config.sweep_id] = Tensorboard(
                    drive=Drive(f"lit://{config.sweep_id}"),
                )
