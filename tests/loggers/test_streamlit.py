import sys
from unittest.mock import MagicMock

from lightning.app.utilities.state import AppState

from lightning_training_studio.loggers.streamlit.hyperplot import HiPlotFlow, render_fn


def test_hiplot(monkeypatch):

    hiplot = MagicMock()
    monkeypatch.setitem(sys.modules, "hiplot", hiplot)

    flow = HiPlotFlow()
    state = AppState()
    state._state = flow.state
    render_fn(state)

    hiplot = MagicMock()
    hiplot.Experiment.from_iterable().to_streamlit().display.return_value = {}
    monkeypatch.setitem(sys.modules, "hiplot", hiplot)

    flow = HiPlotFlow()
    flow.data = [{"a": "1", "b": "2"}]
    state = AppState()
    state._state = flow.state
    render_fn(state)
