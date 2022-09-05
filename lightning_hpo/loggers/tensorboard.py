import os
from typing import Any, Dict, Optional

from lightning import LightningFlow
from lightning.app.storage import Drive

from lightning_hpo.loggers.logger import Logger


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
        from pytorch_lightning.loggers import TensorBoardLogger as PLTensorBoardLogger

        # Create a space logs under the sweep_id folder
        drive = Drive(f"lit://{sweep_id}", component_name="logs")

        use_localhost = "LIGHTNING_APP_STATE_URL" not in os.environ
        save_dir = os.path.join(drive.root, str(trial_id))

        if not use_localhost:
            save_dir = "s3://" + save_dir

        logger = PLTensorBoardLogger(save_dir)
        # logger._fs = filesystem()

        print("Injecting Tensorboard")

        logger.log_hyperparams(params)

        def trainer_pre_fn(trainer, *args, **kwargs):
            kwargs["logger"] = logger
            return {}, args, kwargs

        tracer.add_traced(Trainer, "__init__", pre_fn=trainer_pre_fn)

    def get_url(self, trial_id: int) -> None:
        pass
