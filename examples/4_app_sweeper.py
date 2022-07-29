from lightning import LightningApp

from lightning_hpo.app.sweeper import HPOSweeper

app = LightningApp(HPOSweeper())
