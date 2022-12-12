import urllib.parse
from typing import List

import lightning as L
from lightning.app.api import Post
from lightning.app.storage import Drive

from lightning_training_studio.commands.tensorboard.stop import StopTensorboardConfig, TensorboardConfig
from lightning_training_studio.components.tensorboard import Tensorboard
from lightning_training_studio.controllers.controller import Controller
from lightning_training_studio.utilities.enum import Stage


class TensorboardController(Controller):

    model = TensorboardConfig

    def on_reconcile_start(self, configs: List[TensorboardConfig]):
        for config in configs:
            work_name = urllib.parse.quote_plus(config.sweep_id)
            if work_name not in self.r:
                if config.stage in (Stage.STOPPED, Stage.NOT_STARTED) and config.desired_stage == Stage.RUNNING:
                    self.r[work_name] = Tensorboard(
                        drive=Drive(f"lit://{config.sweep_id}"),
                        config=config,
                        cloud_compute=L.CloudCompute("cpu-small"),
                    )
                    self.r[work_name].stage = Stage.PENDING
            if config.desired_stage == Stage.DELETED:
                tensorboard = self.r[work_name]
                tensorboard.stop()
                self.db.delete(config)
                del self.r[work_name]

    def show_tensorboards(self) -> List[TensorboardConfig]:
        """Show TensorBoards."""
        if self.db_url:
            return self.db.select_all()
        return []

    def run_tensorboard(self, config: TensorboardConfig):
        """Run TensorBoard for a given Sweep or Experiment."""
        tensorboards = self.db.select_all()
        matched_tensorboard = None

        for tensorboard in tensorboards:
            if tensorboard.sweep_id == config.sweep_id:
                matched_tensorboard = config

        if matched_tensorboard:
            matched_tensorboard.stage = Stage.STOPPED
            matched_tensorboard.desired_stage = Stage.RUNNING
            self.db.update(matched_tensorboard)
            return f"Re-Launched a Tensorboard `{config.sweep_id}`."

        self.db.insert(config)
        return f"Launched a Tensorboard `{config.sweep_id}`."

    def stop_tensorboard(self, config: StopTensorboardConfig):
        """Stop TensorBoard for a given Sweep or Experiment."""
        work_name = urllib.parse.quote_plus(config.sweep_id)
        if work_name in self.r:
            self.r[work_name].stop()
            self.r[work_name]._url = ""
            self.r[work_name].stage = Stage.STOPPED
            self.r[work_name].desired_stage = Stage.STOPPED
            self.db.update(self.r[work_name].collect_model())
            del self.r[work_name]
            return f"Tensorboard `{config.sweep_id}` was stopped."
        return f"Tensorboard `{config.sweep_id}` doesn't exist."

    def configure_api(self):
        return [
            Post("/api/run/tensorboard", self.run_tensorboard),
            Post("/api/stop/tensorboard", self.stop_tensorboard),
            Post("/api/show/tensorboards", self.show_tensorboards),
        ]
