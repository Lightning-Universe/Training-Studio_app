import logging

from lightning import LightningApp, LightningFlow

logger = logging.getLogger(__name__)


class RootFlow(LightningFlow):
    def __init__(self):
        super().__init__()

    def run(self):
        from lightning.external_components.lightning_hpo import OptunaPythonScript, BaseObjectiveWork
        print(OptunaPythonScript)
        print(BaseObjectiveWork)
        exit(0)


app = LightningApp(RootFlow())
