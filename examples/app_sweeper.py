from lightning import LightningApp

from lightning_hpo.sweeper import HPOSweeper

app = LightningApp(HPOSweeper())
