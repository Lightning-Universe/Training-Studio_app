from enum import Enum

from lightning_training_studio.loggers.logger import Logger, NoneLogger
from lightning_training_studio.loggers.streamlit.streamlit import StreamLitLogger
from lightning_training_studio.loggers.tensorboard import TensorboardLogger
from lightning_training_studio.loggers.wandb import WandbLogger


class LoggerType(Enum):
    STREAMLIT = "streamlit"
    WANDB = "wandb"
    TENSORBOARD = "tensorboard"
    NONE = "none"

    def get_logger(self) -> Logger:
        if self == LoggerType.NONE:
            return NoneLogger()
        if self == LoggerType.STREAMLIT:
            return StreamLitLogger()
        elif self == LoggerType.WANDB:
            return WandbLogger()
        elif self == LoggerType.TENSORBOARD:
            return TensorboardLogger()
        else:
            raise ValueError("Unknown runtime type")
