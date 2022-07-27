from lightning_hpo.sweeper import HPOSweeper
from lightning import LightningApp

app = LightningApp(HPOSweeper())