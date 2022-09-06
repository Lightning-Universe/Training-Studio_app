from time import sleep
from typing import List

import requests
from lightning.app.frontend import StreamlitFrontend
from lightning.app.storage import Drive
from lightning.app.structures import Dict

from lightning_hpo import Sweep
from lightning_hpo.commands.sweep.delete import DeleteSweepCommand, DeleteSweepConfig
from lightning_hpo.commands.sweep.run import RunSweepCommand, SweepConfig
from lightning_hpo.commands.sweep.show import ShowSweepsCommand
from lightning_hpo.commands.sweep.stop import StopSweepCommand, StopSweepConfig
from lightning_hpo.commands.tensorboard.stop import TensorboardConfig
from lightning_hpo.components.servers.db.models import GeneralModel
from lightning_hpo.controllers.controller import Controller
from lightning_hpo.loggers import LoggerType
from lightning_hpo.utilities.enum import Status


class SweepController(Controller):

    model = SweepConfig
    model_id = "sweep_id"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tensorboard_sweep_id = None

    def on_reconcile_start(self, sweeps: List[SweepConfig]):
        # 1: Retrieve the tensorboard configs from the database
        if self.tensorboard_sweep_id is None:
            self.tensorboard_sweep_id = [c.sweep_id for c in self.db.get(TensorboardConfig)]

        # 2: Create the Sweeps
        for sweep in sweeps:
            id = sweep.sweep_id
            if sweep.logger == LoggerType.TENSORBOARD.value and id not in self.tensorboard_sweep_id:
                self.tensorboard_sweep_id.append(id)
                drive = Drive(f"lit://{id}", component_name="logs")
                self.db.post(TensorboardConfig(sweep_id=id, shared_folder=str(drive.root)), "id")

            if id not in self.resources:
                self.resources[id] = Sweep.from_config(
                    sweep,
                    code={"drive": self.drive, "name": id},
                )

    def on_reconcile_end(self, updates: List[SweepConfig]):
        for update in updates:
            if update.status == Status.SUCCEEDED:
                for w in self.resources[update.sweep_id].works():
                    w.stop()
                self.resources.pop(update.sweep_id)

    def run_sweep(self, config: SweepConfig) -> str:
        sweep_ids = list(self.resources.keys())
        if config.sweep_id not in sweep_ids:
            self.db.post(config)
            return f"Launched a sweep {config.sweep_id}"
        return f"The current Sweep {config.sweep_id} is running. It couldn't be updated."

    def show_sweeps(self) -> List[Dict]:
        return [sweep.json() for sweep in self.db.get()]

    def stop_sweep(self, config: StopSweepConfig):
        sweep_ids = list(self.resources.keys())
        if config.sweep_id in sweep_ids:
            # TODO: Add support for __del__ in lightning
            sweep: Sweep = self.resources[config.sweep_id]
            for w in sweep.works():
                w.stop()
            sweep_config = sweep._sweep_config
            sweep_config.status = Status.STOPPED
            for trial in sweep_config.trials.values():
                if trial.status != Status.SUCCEEDED:
                    trial.status = Status.STOPPED
            self.db.put(sweep_config)
            return f"Stopped the sweep `{config.sweep_id}`"
        return f"We didn't find the sweep `{config.sweep_id}`"

    def delete_sweep(self, config: DeleteSweepConfig):
        sweep_ids = list(self.resources.keys())
        if config.sweep_id in sweep_ids:
            sweep: Sweep = self.resources[config.sweep_id]
            for w in sweep.works():
                w.stop()
            sweep_config = sweep._sweep_config
            self.db.delete(sweep_config)
            del self.resources[config.sweep_id]
            return f"Deleted the sweep `{config.sweep_id}`"
        return f"We didn't find the sweep `{config.sweep_id}`"

    def configure_commands(self):
        return [
            {"delete sweep": DeleteSweepCommand(self.delete_sweep)},
            {"run sweep": RunSweepCommand(self.run_sweep)},
            {"show sweeps": ShowSweepsCommand(self.show_sweeps)},
            {"stop sweep": StopSweepCommand(self.stop_sweep)},
        ]

    def configure_layout(self):
        return StreamlitFrontend(render_fn=render_fn)


def render_fn(state):
    import streamlit as st
    import streamlit.components.v1 as components

    if not state.db_url:
        sleep(1)
        st.experimental_rerun()

    resp = requests.get(state.db_url + "/general/", data=GeneralModel.from_cls(SweepConfig).json())
    sweeps: List[SweepConfig] = resp.json()

    if not sweeps:
        st.header("You haven't launched any sweeps yet.")
        st.write("Here is an example to submit a sweep.")
        st.code(
            'lightning run sweep train.py --n_trials=2 --num_nodes=2 --model.lr="log_uniform(0.001, 0.1)" --trainer.max_epochs=5 --trainer.callbacks=ModelCheckpoint'
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
