import concurrent.futures
import os
from pathlib import Path
from time import time
from typing import Any, Dict, Optional

from lightning_training_studio.utilities.imports import _IS_PYTORCH_LIGHTNING_AVAILABLE

if _IS_PYTORCH_LIGHTNING_AVAILABLE:
    import pytorch_lightning
    from pytorch_lightning.loggers import TensorBoardLogger
else:
    import lightning.pytorch as pytorch_lightning
    from lightning.pytorch.loggers import TensorBoardLogger

from fsspec.implementations.local import LocalFileSystem
from lightning import LightningFlow
from lightning.app.storage import Drive
from lightning.app.storage.path import _filesystem

from lightning_training_studio.loggers.logger import Logger


class DriveTensorBoardLogger(TensorBoardLogger):
    def __init__(self, *args, drive: Drive, refresh_time: int = 5, **kwargs):
        super().__init__(*args, **kwargs)
        self.timestamp = None
        self.drive = drive
        self.refresh_time = refresh_time

    def log_metrics(self, metrics, step) -> None:
        super().log_metrics(metrics, step)
        if self.timestamp is None:
            self._upload_to_storage()
            self.timestamp = time()
        elif (time() - self.timestamp) > self.refresh_time:
            self._upload_to_storage()
            self.timestamp = time()

    def finalize(self, status: str) -> None:
        super().finalize(status)

    def _upload_to_storage(self):
        fs = _filesystem()
        fs.invalidate_cache()

        source_path = Path(self.log_dir).resolve()
        destination_path = self.drive._to_shared_path(self.log_dir, component_name=self.drive.component_name)

        def _copy(from_path: Path, to_path: Path) -> Optional[Exception]:

            try:
                # NOTE: S3 does not have a concept of directories, so we do not need to create one.
                if isinstance(fs, LocalFileSystem):
                    fs.makedirs(str(to_path.parent), exist_ok=True)

                fs.put(str(from_path), str(to_path), recursive=False)

                # Don't delete tensorboard logs.
                if "events.out.tfevents" not in str(from_path):
                    os.remove(str(from_path))

            except Exception as e:
                # Return the exception so that it can be handled in the main thread
                return e

        src = [file for file in source_path.rglob("*") if file.is_file()]
        dst = [destination_path / file.relative_to(source_path) for file in src]

        with concurrent.futures.ThreadPoolExecutor(4) as executor:
            results = executor.map(_copy, src, dst)

        # Raise the first exception found
        exception = next((e for e in results if isinstance(e, Exception)), None)
        if exception:
            raise exception


class TensorboardLogger(Logger):
    def on_after_experiment_start(self, sweep_id: str, title: Optional[str] = None, desc: Optional[str] = None):
        pass

    def on_after_experiment_end(
        self, sweep_id: str, experiment_id: int, monitor: str, score: float, params: Dict[str, Any]
    ):
        pass

    def connect(self, flow: LightningFlow):
        pass

    def configure_layout(self):
        return []

    def configure_tracer(self, tracer, sweep_id: str, experiment_id: int, experiment_name: str, params: Dict[str, Any]):
        # Create a space logs under the sweep_id folder
        drive = Drive(f"lit://{sweep_id}", component_name=experiment_name, allow_duplicates=True)
        use_localhost = "LIGHTNING_APP_STATE_URL" not in os.environ

        if use_localhost:
            logger = TensorBoardLogger(save_dir=str(drive.root), name="", version="")
        else:
            logger = DriveTensorBoardLogger(save_dir=".", name="", drive=drive, refresh_time=1)

        # TODO: Collect the monitor + metric at the end.
        logger.log_hyperparams(params)

        def trainer_pre_fn(trainer, *args, **kwargs):
            kwargs["logger"] = logger
            return {}, args, kwargs

        tracer.add_traced(pytorch_lightning.Trainer, "__init__", pre_fn=trainer_pre_fn)

    def get_url(self, experiment_id: int) -> None:
        pass
