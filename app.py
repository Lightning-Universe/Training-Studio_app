from lightning import LightningApp

from lightning_hpo.app.main import ResearchStudio

app = LightningApp(ResearchStudio())
