import sys
from typing import List

from lightning.app.utilities.commands import ClientCommand
from rich.console import Console
from rich.table import Table

from lightning_training_studio.commands.sweep.run import SweepConfig


def _show_experiments(sweeps: List[SweepConfig]):
    table = Table(
        "name",
        "cloud compute",
        "progress",
        "best model score",
        "sweep name",
        title="Experiments",
        show_header=True,
        header_style="bold green",
    )

    for sweep in sweeps:
        experiments = sweep.experiments.values()
        for experiment in experiments:
            table.add_row(
                str(experiment.name),
                sweep.cloud_compute,
                str(experiment.progress) if experiment.stage != "failed" else "failed",
                str(round(experiment.best_model_score, 2) if experiment.best_model_score else None),
                None if len(experiments) == 1 else sweep.sweep_id,
            )
    console = Console()
    console.print(table)


class ShowExperimentsCommand(ClientCommand):

    description = "Show experiments and their statuses."

    def run(self) -> None:
        if sys.argv and sys.argv[-1] == "--help":
            print("optional arguments:")
            print("  -h, --help   show this help message and exit")
            return

        # 1: Collect the SweepConfig
        resp = self.invoke_handler()

        # 3: Display the Sweeps or Sweep
        # TODO: Undestand why the format isn't the same
        try:
            sweeps = [SweepConfig.parse_raw(sweep) for sweep in resp]
        except Exception:
            sweeps = [SweepConfig(**sweep) for sweep in resp]

        _show_experiments(sweeps)
