from lightning import LightningFlow
from lightning_hpo.loggers.base import Logger
from lightning_hpo.loggers.streamlit.hyperplot import HiPlotFlow
from typing import Dict, Any

class StreamLitLogger(Logger):

    def __init__(self):
        super().__init__()
        self.hi_plot = HiPlotFlow()

    def on_trial_start(self, *_):
        pass

    def on_trial_end(self, score: float, params: Dict[str, Any]):
        self.hi_plot.data.append({"score": score, **params})

    def connect(self, flow: LightningFlow):
        flow.hi_plot = self.hi_plot

    def configure_layout(self):
        return  [{"name": "Experiment", "content": self.hi_plot}]

    def configure_tracer(self, tracer, params: Dict[str, Any], trial_id: int):
        pass