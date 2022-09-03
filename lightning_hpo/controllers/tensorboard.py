from lightning_hpo.commands.tensorboard.stop import TensorboardConfig
from lightning_hpo.controllers.controller import Controller


class TensorboardController(Controller):

    model = TensorboardConfig

    def on_reconcile_start(self, configs):
        breakpoint()
