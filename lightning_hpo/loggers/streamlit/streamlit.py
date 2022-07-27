from lightning import LightningFlow
from lightning_hpo.loggers.base import Logger
from lightning_hpo.loggers.streamlit.hyperplot import HiPlotFlow
from typing import Dict, Any

class StreamLitLogger(Logger):

    def __init__(self):
        super().__init__()
        self.hi_plot = HiPlotFlow()

    def on_start(self, sweep_id: str):
        return super().on_start(sweep_id)

    def on_trial_end(self, score: float, params: Dict[str, Any]):
        self.hi_plot.data.append({"score": score, **params})

    def on_batch_trial_end(self):
        return super().on_batch_trial_end()

    def connect(self, flow: LightningFlow):
        flow.hi_plot = self.hi_plot

    def configure_layout(self):
        return  [{"name": "Experiment", "content": self.hi_plot}]