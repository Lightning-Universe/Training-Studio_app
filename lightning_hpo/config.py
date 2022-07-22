import os
import sys
from dataclasses import dataclass
from optuna.distributions import LogUniformDistribution, UniformDistribution
from lightning.pytorch.loggers import LightningLoggerBase
from rich import print as rprint


def validate_logger():
    logger = os.environ.get("LOGGER")
    if logger is not None:
        logger = logger.upper()
    if not hasattr(Loggers, logger):
        rprint(
            "\n\n"
            + f"You are trying to use [bold green]{logger}[/bold green], which is an unsupported logger."
            + "\n"
        )
        rprint(
            f"Supported loggers are: {', '.join([l for l in dir(Loggers) if not l.startswith('_')])}"
            + "\n"
        )
        sys.exit()


class Loggers:
    WANDB = "wandb"
    STREAMLIT = "streamlit"


@dataclass
class BaseConfig:
    def __init__(self):
        super().__init__()

    @staticmethod
    def validate_auth():
        if os.getenv("WANDB_API_KEY") is None or os.getenv("WANDB_ENTITY") is None:
            rprint(
                "\n\n"
                + "You are trying to use wandb without setting your API key or entity. Please set your wandb config with:"
                + "\n"
            )
            rprint(
                "lightning run app app_name.py --env LOGGER=wandb --env WANDB_API_KEY=YOUR_API_KEY"
                + "\n\n"
            )
            sys.exit()

    @classmethod
    def get_sweep_config(cls, distributions):

        parameters = {}
        for k, d in distributions.items():
            parameters[k] = {}
            distribution_name = cls._to_distribution_name(d)
            if distribution_name:
                parameters[k]["distribution"] = distribution_name
            parameters[k].update(cls._to_distribution_values(d))

        sweep_config = {
            "method": "random",
            "metric": {"name": "loss", "goal": "minimize"},
            "parameters": parameters,
        }

        return sweep_config

    @staticmethod
    def _to_distribution_name(d):
        if isinstance(d, LogUniformDistribution):
            return "q_log_uniform_values"
        elif isinstance(d, UniformDistribution):
            return "uniform"
        return

    @staticmethod
    def _to_distribution_values(d):
        if isinstance(d, (LogUniformDistribution, UniformDistribution)):
            return {"min": d.low, "max": d.high}
        return [v for v in d.choices]
