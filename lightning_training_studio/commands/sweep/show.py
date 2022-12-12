import argparse
from typing import Any, Dict, List, Optional

import requests
from lightning.app.utilities.commands import ClientCommand
from pydantic import BaseModel
from rich.console import Console
from rich.table import Table

from lightning_training_studio.commands.sweep.run import SweepConfig


def _show_sweeps(sweeps: List[SweepConfig]):
    table = Table(
        "name",
        "cloud compute",
        "total experiments",
        "total experiments done",
        title="Sweep",
        show_header=True,
        header_style="bold green",
    )

    for sweep in sweeps:
        table.add_row(
            sweep.sweep_id,
            sweep.cloud_compute,
            str(sweep.total_experiments),
            str(sweep.total_experiments_done),
        )

    console = Console()
    console.print(table)


class ShowSweepsCommand(ClientCommand):

    description = "Show all sweeps and their statuses, or the experiments for a given sweep."

    # TODO: (tchaton) Upstream to Lightning
    def invoke_handler(self, config: Optional[BaseModel] = None) -> Dict[str, Any]:
        command = self.command_name.replace(" ", "_")
        resp = requests.post(self.app_url + f"/command/{command}", data=config.json() if config else None)
        assert resp.status_code == 200, resp.json()
        return resp.json()

    def run(self) -> None:
        # 1. Parse the user arguments.
        parser = argparse.ArgumentParser()
        parser.add_argument("--name", type=str, default=None, help="Provide the `name` to be showed.")
        hparams = parser.parse_args()

        # 2: Collect the SweepConfig
        resp = self.invoke_handler()

        # 3: Display the Sweeps or Sweep
        # TODO: Undestand why the format isn't the same
        try:
            sweeps = [SweepConfig.parse_raw(sweep) for sweep in resp]
        except Exception:
            sweeps = [SweepConfig(**sweep) for sweep in resp]

        if hparams.name is None:
            _show_sweeps(sweeps)
        else:
            matching_sweep = [sweep for sweep in sweeps if sweep.sweep_id == hparams.name]
            if not matching_sweep:
                raise Exception(
                    "The provided `sweep_id` doesn't exists. "
                    f"Here are the available ones {[s.sweep_id for s in sweeps]}"
                )
            assert len(matching_sweep) == 1
            _show_sweeps(matching_sweep)
