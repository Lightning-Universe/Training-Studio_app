from lightning import LightningApp

from lightning_hpo.app.main import MainFlow

app = LightningApp(MainFlow())
