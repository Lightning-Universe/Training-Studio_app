from typing import Optional

import optuna
from lightning import BuildConfig, LightningFlow
from lightning.app.frontend import StreamlitFrontend
from lightning.app.storage import Drive
from lightning.app.storage.path import Path
from lightning.app.structures import Dict

from lightning_hpo import Sweep
from lightning_hpo.algorithm import OptunaAlgorithm
from lightning_hpo.commands.sweep import SweepCommand, SweepConfig
from lightning_hpo.components.servers.file_server import FileServer
from lightning_hpo.utilities.utils import CloudCompute, get_best_model_path


class Sweeper(LightningFlow):
    def __init__(self):
        super().__init__()
        self.sweeps = Dict()
        self.drive = Drive("lit://code")
        self.file_server = FileServer(self.drive)

    def run(self):
        self.file_server.run()
        if self.file_server.alive():
            for sweep in self.sweeps.values():
                sweep.run()

    def create_sweep(self, config: SweepConfig) -> str:
        sweep_ids = list(self.sweeps.keys())
        if config.sweep_id not in sweep_ids:
            self.sweeps[config.sweep_id] = Sweep(
                script_path=config.script_path,
                n_trials=config.n_trials,
                simultaneous_trials=config.simultaneous_trials,
                framework=config.framework,
                script_args=config.script_args,
                distributions=config.distributions,
                cloud_compute=CloudCompute(config.cloud_compute, config.num_nodes),
                sweep_id=config.sweep_id,
                code={"drive": self.drive, "name": config.sweep_id},
                cloud_build_config=BuildConfig(requirements=config.requirements),
                logger=config.logger,
                algorithm=OptunaAlgorithm(optuna.create_study(direction=config.direction)),
            )
            return f"Launched a sweep {config.sweep_id}"
        elif self.sweeps[config.sweep_id].has_failed:
            self.sweeps[config.sweep_id].restart_count += 1
            self.sweeps[config.sweep_id].has_failed = False
            return f"Updated code for Sweep {config.sweep_id}."
        else:
            return f"The current Sweep {config.sweep_id} is running. It couldn't be updated."

    def configure_commands(self):
        return [{"sweep": SweepCommand(self.create_sweep)}]

    @property
    def best_model_score(self) -> Optional[Path]:
        return get_best_model_path(self)

    def configure_layout(self):
        return StreamlitFrontend(render_fn=render_fn)


def render_fn(state):
    import streamlit as st

    sweeps = state.sweeps.items()
    if not sweeps:
        st.header("You haven't launched any sweeps yet.")
        st.write("Here is an example to submit a sweep.")
        st.code(
            'lightning sweep train.py --n_trials=2 --num_nodes=2 --model.lr="log_uniform(0.001, 0.1)" --trainer.max_epochs=5 --trainer.callbacks=ModelCheckpoint'
        )
        return

    user_sweeps = {}
    for sweep_id, sweep in sweeps:
        username = sweep_id.split("-")[0]
        if username not in user_sweeps:
            user_sweeps[username] = {}
        user_sweeps[username][sweep_id] = sweep

    user_tabs = st.tabs(list(user_sweeps))
    for tab, username, sweep_id in zip(user_tabs, user_sweeps, user_sweeps):
        with tab:
            for sweep_id, sweep in user_sweeps[username].items():
                status = "/ failed" if sweep.has_failed else ""
                with st.expander(f"{sweep_id} {status}"):
                    show_report = st.checkbox("Report", value=sweep.show, key=f"report_{sweep_id}")
                    if show_report:
                        sweep.show = True
                    else:
                        sweep.show = False
                    for trial_id, trial in sweep.items():
                        if st.checkbox(f"Trial {trial_id}", key=f"checkbox_{trial_id}_{sweep_id}"):
                            tab1, tab2, tab3 = st.tabs(["Script Args", "Hyper-Parameters", "Results"])
                            with tab1:
                                st.code(trial.script_args)
                            with tab2:
                                st.json(trial.params)
                            with tab3:
                                try:
                                    st.json({"best_model_score": trial.ws["0"].best_model_score})
                                except Exception:
                                    pass


class HPOSweeper(LightningFlow):
    def __init__(self):
        super().__init__()
        self.sweeper = Sweeper()

    def run(self):
        self.sweeper.run()

    def configure_layout(self):
        tabs = [{"name": "Team Control", "content": self.sweeper}]
        for sweep in self.sweeper.sweeps.values():
            if sweep.show:
                tabs += sweep.configure_layout()
        return tabs

    def configure_commands(self):
        return self.sweeper.configure_commands()
