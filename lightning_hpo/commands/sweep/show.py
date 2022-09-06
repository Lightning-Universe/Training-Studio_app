import argparse
from typing import Any, Dict, List, Optional

import requests
from lightning.app.utilities.commands import ClientCommand
from pydantic import BaseModel
from rich.console import Console
from rich.table import Table

from lightning_hpo.commands.sweep.run import SweepConfig


def _show_sweeps(sweeps: List[SweepConfig]):
    table = Table(
        "id",
        "status",
        "framework",
        "cloud_compute",
        "n_trials",
        "n_trials_done",
        title="Sweeps",
        show_header=True,
        header_style="bold green",
    )

    for sweep in sweeps:
        table.add_row(
            sweep.sweep_id,
            sweep.status,
            sweep.framework,
            sweep.cloud_compute,
            str(sweep.n_trials),
            str(sweep.trials_done),
        )
    console = Console()
    console.print(table)


def _show_sweep(sweep: SweepConfig):
    table = Table(
        "id",
        "status",
        "framework",
        "cloud_compute",
        "n_trials",
        "n_trials_done",
        title="Sweep",
        show_header=True,
        header_style="bold green",
    )

    table.add_row(
        sweep.sweep_id,
        sweep.status,
        sweep.framework,
        sweep.cloud_compute,
        str(sweep.n_trials),
        str(sweep.trials_done),
    )
    console = Console()
    console.print(table)

    table = Table(
        "id",
        "status",
        "best_model_score",
        "params",
        "monitor",
        title="Trials",
        show_header=True,
        header_style="bold green",
    )

    for idx, trial in sweep.trials.items():
        table.add_row(
            str(idx),
            str(trial.status),
            str(round(trial.best_model_score, 2) if trial.best_model_score else None),
            str({k: round(v, 5) for k, v in trial.params.params.items()}),
            str(trial.monitor),
        )
    console = Console()
    console.print(table)


class ShowSweepsCommand(ClientCommand):

    DESCRIPTION = "Command to show a Sweep or its Trials"

    # TODO: (tchaton) Upstream to Lightning
    def invoke_handler(self, config: Optional[BaseModel] = None) -> Dict[str, Any]:
        command = self.command_name.replace(" ", "_")
        resp = requests.post(self.app_url + f"/command/{command}", data=config.json() if config else None)
        assert resp.status_code == 200, resp.json()
        return resp.json()

    def run(self) -> None:
        # 1. Parse the user arguments.
        parser = argparse.ArgumentParser()
        parser.add_argument("--sweep_id", type=str, default=None, help="Provide the `sweep_id` to be showed.")
        hparams = parser.parse_args()

        # 2: Collect the SweepConfig
        resp = self.invoke_handler()

        # 3: Display the Sweeps or Sweep
        # TODO: Undestand why the format isn't the same
        try:
            sweeps = [SweepConfig.parse_raw(sweep) for sweep in resp]
        except Exception:
            sweeps = [SweepConfig(**sweep) for sweep in resp]

        if hparams.sweep_id is None:
            _show_sweeps(sweeps)
        else:
            matching_sweep = [sweep for sweep in sweeps if sweep.sweep_id == hparams.sweep_id]
            if not matching_sweep:
                raise Exception(
                    "The provided `sweep_id` doesn't exists. "
                    f"Here are the available ones {[s.sweep_id for s in sweeps]}"
                )
            assert len(matching_sweep) == 1
            _show_sweep(*matching_sweep)
