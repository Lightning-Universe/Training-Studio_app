from lightning import LightningFlow
from lightning.app.frontend.stream_lit import StreamlitFrontend
from lightning.app.utilities.state import AppState


class HiPlotFlow(LightningFlow):
    def __init__(self):
        super().__init__()
        """TO BE IMPLEMENTED"""

    def configure_layout(self):
        return StreamlitFrontend(render_fn=render_fn)


def render_fn(state: AppState):
    """TO BE IMPLEMENTED"""

