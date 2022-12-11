from typing import Any, Dict

from lightning import LightningFlow

from lightning_training_studio.loggers.logger import Logger
from lightning_training_studio.loggers.streamlit.hyperplot import HiPlotFlow


class StreamLitLogger(Logger):
    def __init__(self):
        super().__init__()
        self.hi_plot = HiPlotFlow()

    def on_after_experiment_end(
        self, sweep_id: str, experiment_id: int, monitor: str, score: float, params: Dict[str, Any]
    ):
        self.hi_plot.data.append({monitor: score, **params})

    def connect(self, flow: LightningFlow):
        flow.hi_plot = self.hi_plot

    def configure_layout(self):
        return [{"name": "Experiment", "content": self.hi_plot}]

    def configure_tracer(self, tracer, sweep_id: str, experiment_id: int, experiment_name: str, params: Dict[str, Any]):
        pass

    def get_url(self, experiment_id: int) -> None:
        return None
