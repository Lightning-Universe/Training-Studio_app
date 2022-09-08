from typing import List

from lightning.app.storage import Drive

from lightning_hpo.commands.tensorboard.stop import StopTensorboardConfig, TensorboardConfig
from lightning_hpo.components.tensorboard import Tensorboard
from lightning_hpo.controllers.controller import Controller
from lightning_hpo.utilities.enum import Status


class TensorboardController(Controller):

    model = TensorboardConfig

    def on_reconcile_start(self, configs: List[TensorboardConfig]):
        for config in configs:
            if config.sweep_id not in self.r:
                if config.status in (Status.STOPPED, Status.NOT_STARTED) and config.desired_state == Status.RUNNING:
                    self.r[config.sweep_id] = Tensorboard(
                        drive=Drive(f"lit://{config.sweep_id}"),
                        config=config,
                    )

    def show_tensorboards(self) -> List[TensorboardConfig]:
        if self.db_url:
            return self.db.get()
        return []

    def run_tensorboard(self, config: TensorboardConfig):
        tensorboards = self.db.get()
        matched_tensorboard = None

        for tensorboard in tensorboards:
            if tensorboard.sweep_id == config.sweep_id:
                matched_tensorboard = config

        if matched_tensorboard:
            matched_tensorboard.status = Status.STOPPED
            matched_tensorboard.desired_state = Status.RUNNING
            self.db.put(matched_tensorboard)
            return f"Re-Launched a Tensorboard `{config.sweep_id}`."

        self.db.post(config)
        return f"Launched a Tensorboard `{config.sweep_id}`."

    def stop_tensorboard(self, config: StopTensorboardConfig):
        if config.sweep_id in self.r:
            self.r[config.sweep_id].stop()
            self.r[config.sweep_id]._config.url = None
            self.r[config.sweep_id]._config.status = Status.STOPPED
            self.r[config.sweep_id]._config.desired_state = Status.STOPPED
            self.db.put(self.r[config.sweep_id]._config)
            del self.r[config.sweep_id]
            return f"Tensorboard `{config.sweep_id}` was stopped."
        return f"Tensorboard `{config.sweep_id}` doesn't exist."

    def configure_commands(self):
        return [
            {"run tensorboard": self.run_tensorboard},
            {"show tensorboards": self.show_tensorboards},
            {"stop tensorboard": self.stop_tensorboard},
        ]
