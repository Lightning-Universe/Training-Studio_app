from lightning import LightningFlow
from lightning.frontend.stream_lit import StreamlitFrontend
from lightning.utilities.state import AppState


class HiPlotFlow(LightningFlow):
    def __init__(self):
        super().__init__()
        """TO BE IMPLEMENTED"""

    def configure_layout(self):
        return StreamlitFrontend(render_fn=render_fn)


def render_fn(state: AppState):
    """TO BE IMPLEMENTED"""

