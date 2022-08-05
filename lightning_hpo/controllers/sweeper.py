from typing import List, Optional

import requests
from lightning import LightningFlow
from lightning.app.frontend import StreamlitFrontend
from lightning.app.storage import Drive
from lightning.app.storage.path import Path
from lightning.app.structures import Dict

from lightning_hpo import Sweep
from lightning_hpo.commands.sweep import SweepCommand, SweepConfig
from lightning_hpo.components.servers.db.models import GeneralModel
from lightning_hpo.components.servers.file_server import FileServer
from lightning_hpo.utilities.enum import Status
from lightning_hpo.utilities.utils import get_best_model_path


class SweepController(LightningFlow):
    def __init__(self, drive: Drive, use_db_viz: bool = True):
        super().__init__()
        self.sweeps = Dict()
        self.drive = drive
        self.file_server = FileServer(self.drive)
        self.db_url = None

    def run(self, db_url: str):
        self.db_url = db_url

        # 1: Read from the database and generate the works accordingly.
        # TODO: Improve the schedule API.
        if self.schedule("* * * * * 0,5,10,15,20,25,30,35,40,45,50,55"):
            self.reconcile_sweeps_on_start()

        # 2: Iterate over the sweeps and collect updates
        updates = []
        for sweep in self.sweeps.values():
            sweep.run()
            updates.extend(sweep.updates)

        # 3: Reconcile sweep on end
        self.reconcile_sweep_on_end(updates)

    def reconcile_sweeps_on_start(self):
        resp = requests.get(self.db_url + "/general/", data=GeneralModel.from_cls(SweepConfig).json())
        assert resp.status_code == 200
        sweeps = [SweepConfig(**sweep) for sweep in resp.json()]
        for config in sweeps:
            if config.trials_done == config.n_trials:
                continue
            if config.sweep_id not in self.sweeps:
                self.sweeps[config.sweep_id] = Sweep.from_config(
                    config,
                    code={"drive": self.drive, "name": config.sweep_id},
                )

    def reconcile_sweep_on_end(self, updates: List[SweepConfig]):
        for update in updates:
            resp = requests.put(self.db_url + "/general/", data=GeneralModel.from_obj(update, id="sweep_id").json())
            assert resp.status_code == 200
            if update.status == Status.SUCCEEDED:
                for w in self.sweeps.works:
                    w.stop()
                self.sweeps.pop(update.sweep_id)

    def sweep_handler(self, config: SweepConfig) -> str:
        sweep_ids = list(self.sweeps.keys())
        if config.sweep_id not in sweep_ids:
            resp = requests.post(self.db_url + "/general/", data=GeneralModel.from_obj(config).json())
            assert resp.status_code == 200
            return f"Launched a sweep {config.sweep_id}"
        elif self.sweeps[config.sweep_id].has_failed:
            self.sweeps[config.sweep_id].restart_count += 1
            self.sweeps[config.sweep_id].has_failed = False
            return f"Updated code for Sweep {config.sweep_id}."
        else:
            return f"The current Sweep {config.sweep_id} is running. It couldn't be updated."

    def configure_commands(self):
        return [
            {"sweep": SweepCommand(self.sweep_handler)},
        ]

    @property
    def best_model_score(self) -> Optional[Path]:
        return get_best_model_path(self)

    def configure_layout(self):
        return StreamlitFrontend(render_fn=render_fn)


def render_fn(state):
    import streamlit as st
    import streamlit.components.v1 as components

    resp = requests.get(state.db_url + "/general/", data=GeneralModel.from_cls(SweepConfig).json())
    sweeps: List[SweepConfig] = resp.json()

    if not sweeps:
        st.header("You haven't launched any sweeps yet.")
        st.write("Here is an example to submit a sweep.")
        st.code(
            'lightning sweep train.py --n_trials=2 --num_nodes=2 --model.lr="log_uniform(0.001, 0.1)" --trainer.max_epochs=5 --trainer.callbacks=ModelCheckpoint'
        )
        return

    user_sweeps = {}
    for sweep in sweeps:
        username, sweep_id = sweep["sweep_id"].split("-")
        if username not in user_sweeps:
            user_sweeps[username] = {}
        user_sweeps[username][sweep_id] = sweep

    user_tabs = st.tabs(user_sweeps)
    for tab, username in zip(user_tabs, user_sweeps):
        with tab:
            for sweep_id, sweep in user_sweeps[username].items():
                with st.expander(f"{sweep_id} / {sweep['status']}"):
                    trials_tab, logging_tab = st.tabs(["Trials", "Logging"])
                    with trials_tab:
                        for trial_id, trial in sweep["trials"].items():
                            if st.checkbox(f"Trial {trial_id}", key=f"checkbox_{trial_id}_{sweep_id}"):
                                st.json(
                                    {
                                        "params": trial["params"]["params"],
                                        "monitor": trial["monitor"],
                                        "best_model_score": trial["best_model_score"],
                                    }
                                )
                            with logging_tab:
                                url = trial.get("url", None)
                                if url:
                                    components.html(
                                        f'<a href="{url}" target="_blank">Weights & Biases URL</a>', height=50
                                    )
