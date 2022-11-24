from lightning import LightningApp

from lightning_hpo.app.main import TrainingStudio

app = LightningApp(TrainingStudio())
