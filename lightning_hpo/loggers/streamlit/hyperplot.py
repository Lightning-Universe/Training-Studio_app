from lightning import LightningFlow
from lightning.app.frontend.stream_lit import StreamlitFrontend
from lightning.app.utilities.state import AppState


class HiPlotFlow(LightningFlow):
    def __init__(self):
        super().__init__()
        self.data = []

    def configure_layout(self):
        return StreamlitFrontend(render_fn=render_fn)


def render_fn(state: AppState):
    import json

    import hiplot as hip
    import streamlit as st

    st.set_page_config(layout="wide")

    if not state.data:
        st.write("No data available yet ! Stay tuned")
        return

    xp = hip.Experiment.from_iterable(state.data)
    ret_val = xp.to_streamlit(ret="selected_uids", key="hip").display()
    st.markdown("hiplot returned " + json.dumps(ret_val))
