from lightning.pytorch.loggers import WandbLogger
from lightning_hpo.loggers import BaseConfig


class Wandb(BaseConfig, WandbLogger):
    def __init__(self):
        super().__init__()

    @classmethod
    def get_sweep_config(cls, distributions):

        parameters = {}
        for k, d in distributions.items():
            parameters[k] = {}
            distribution_name = cls._to_distribution_name(d)
            if distribution_name:
                parameters[k]['distribution'] = distribution_name
            parameters[k].update(cls._to_distribution_values(d))

        sweep_config = {
            'method': 'random',
            'metric': {
                'name': 'loss',
                'goal': 'minimize'
            },
            'parameters': parameters
        }

        return sweep_config