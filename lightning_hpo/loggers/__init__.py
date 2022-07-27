from enum import Enum
from lightning_hpo.loggers.streamlit.streamlit import StreamLitLogger
from lightning_hpo.loggers.wandb import WandB
from typing import Type
from lightning_hpo.loggers.base import Logger

class LoggerType(Enum):
    STREAMLIT = "streamlit"
    WANDB = "wandb"

    def get_logger(self) -> Logger:
        if self == LoggerType.STREAMLIT:
            return StreamLitLogger()
        elif self == LoggerType.WANDB:
            return WandB()
        else:
            raise ValueError("Unknown runtime type")