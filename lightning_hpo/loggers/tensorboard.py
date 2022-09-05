import os
from time import time
from typing import Any, Dict, Optional

from lightning import LightningFlow
from lightning.app.storage import Drive
from lightning.pytorch.loggers import TensorBoardLogger
from lightning.pytorch.utilities.rank_zero import rank_zero_only

from lightning_hpo.loggers.logger import Logger


class DriveTensorBoardLogger(TensorBoardLogger):
    def __init__(self, *args, drive: Drive, refresh_time: int = 5, **kwargs):
        super().__init__(*args, **kwargs)
        self.timestamp = None
        self.drive = drive
        self.refresh_time = refresh_time

    @rank_zero_only
    def log_metrics(self, metrics, step) -> None:
        super().log_metrics(metrics, step)
        if self.timestamp is None:
            self.drive.put(self.log_dir)
            self.timestamp = time()
        elif (time() - self.timestamp) > self.refresh_time:
            self.drive.put(self.log_dir)
            self.timestamp = time()

    @rank_zero_only
    def finalize(self, status: str) -> None:
        super().finalize(status)
        self.drive.put(self.log_dir)


class TensorboardLogger(Logger):
    def on_after_trial_start(self, sweep_id: str, title: Optional[str] = None, desc: Optional[str] = None):
        pass

    def on_after_trial_end(self, sweep_id: str, trial_id: int, monitor: str, score: float, params: Dict[str, Any]):
        pass

    def connect(self, flow: LightningFlow):
        pass

    def configure_layout(self):
        return []

    def configure_tracer(self, tracer, sweep_id: str, trial_id: int, params: Dict[str, Any]):
        from pytorch_lightning import Trainer

        # Create a space logs under the sweep_id folder
        drive = Drive("lit://logs", component_name=f"{sweep_id}/{trial_id}")
        use_localhost = "LIGHTNING_APP_STATE_URL" not in os.environ

        if use_localhost:
            logger = TensorBoardLogger(save_dir=str(drive.root))
        else:
            logger = DriveTensorBoardLogger(save_dir=".", name="", drive=drive, refresh_time=5)

        print("Injecting Tensorboard")

        logger.log_hyperparams(params)

        def trainer_pre_fn(trainer, *args, **kwargs):
            kwargs["logger"] = logger
            return {}, args, kwargs

        tracer.add_traced(Trainer, "__init__", pre_fn=trainer_pre_fn)

    def get_url(self, trial_id: int) -> None:
        pass
