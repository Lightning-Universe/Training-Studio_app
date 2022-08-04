from typing import List, Optional

import requests
from lightning import LightningFlow
from lightning.app.frontend import StreamlitFrontend
from lightning.app.storage import Drive
from lightning.app.storage.path import Path
from lightning.app.structures import Dict

from lightning_hpo import Sweep
from lightning_hpo.commands.sweep import SweepCommand, SweepConfig
from lightning_hpo.components.servers.db.server import Database
from lightning_hpo.components.servers.db.visualization import DatabaseViz
from lightning_hpo.components.servers.file_server import FileServer
from lightning_hpo.utilities.enum import Status
from lightning_hpo.utilities.utils import get_best_model_path


class Sweeper(LightningFlow):
    def __init__(self, use_db_viz: bool = True):
        super().__init__()
        self.sweeps = Dict()
        self.drive = Drive("lit://code")
        self.file_server = FileServer(self.drive)
        self.db = Database()
        self.db_viz = DatabaseViz()

    def run(self):
        # 1: Start the servers.
        self.file_server.run()
        self.db.run()
        self.db_viz.run()

        # 2: Wait for the servers to be alive
        if not (self.file_server.alive() and self.db.alive()):
            return

        # 3: Read from the database and generate the works accordingly.
        # TODO: Improve the schedule API.
        if self.schedule("* * * * * 0,5,10,15,20,25,30,35,40,45,50,55"):
            self.reconcile_sweeps_on_start()

        # 4: Iterate over the sweeps and collect updates
        updates = []
        for sweep in self.sweeps.values():
            sweep.run()
            updates.extend(sweep.updates)

        # 5: Reconcile sweep on end
        self.reconcile_sweep_on_end(updates)

    def reconcile_sweeps_on_start(self):
        resp = requests.get(self.db.url + "/reconcile_sweeps/")
        assert resp.status_code == 200
        sweeps = [SweepConfig(**sweep) for sweep in resp.json()]
        for config in sweeps:
            if config.sweep_id not in self.sweeps:
                self.sweeps[config.sweep_id] = Sweep.from_config(
                    config,
                    code={"drive": self.drive, "name": config.sweep_id},
                )

    def reconcile_sweep_on_end(self, updates: List[SweepConfig]):
        for update in updates:
            resp = requests.put(self.db.url + "/sweep/", data=update.json())
            assert resp.status_code == 200
            if update.status == Status.SUCCEEDED:
                for w in self.sweeps.works:
                    w.stop()
                self.sweeps.pop(update.sweep_id)

    def sweep_handler(self, config: SweepConfig) -> str:
        sweep_ids = list(self.sweeps.keys())
        if config.sweep_id not in sweep_ids:
            resp = requests.post(self.db.url + "/sweep", data=config.json())
            assert resp.status_code == 200
            return f"Launched a sweep {config.sweep_id}"
        elif self.sweeps[config.sweep_id].has_failed:
            self.sweeps[config.sweep_id].restart_count += 1
            self.sweeps[config.sweep_id].has_failed = False
            return f"Updated code for Sweep {config.sweep_id}."
        else:
            return f"The current Sweep {config.sweep_id} is running. It couldn't be updated."

    def configure_commands(self):
        return [{"sweep": SweepCommand(self.sweep_handler)}]

    @property
    def best_model_score(self) -> Optional[Path]:
        return get_best_model_path(self)

    def configure_layout(self):
        return StreamlitFrontend(render_fn=render_fn)


def render_fn(state):
    import streamlit as st
    import streamlit.components.v1 as components

    database_url = state.db._state["vars"]["_url"] + "/sweep/"
    resp: requests.Response = requests.get(database_url)
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


class HPOSweeper(LightningFlow):
    def __init__(self):
        super().__init__()
        self.sweeper = Sweeper()

    def run(self):
        self.sweeper.run()

    def configure_layout(self):
        tabs = [{"name": "Team Control", "content": self.sweeper}]
        tabs += [{"name": "Database Viz", "content": self.sweeper.db_viz}]
        for sweep in self.sweeper.sweeps.values():
            if sweep.show:
                tabs += sweep.configure_layout()
        return tabs

    def configure_commands(self):
        return self.sweeper.configure_commands()
