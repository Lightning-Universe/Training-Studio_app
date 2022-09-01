import abc
import argparse
from typing import List

from lightning.app.utilities.commands import ClientCommand
from rich.console import Console
from rich.table import Table

from lightning_hpo.commands.sweep.run_sweep import SweepConfig


class Formatable(abc.ABC):
    @abc.abstractmethod
    def as_table(self) -> Table:
        pass


class SweepsList(Formatable):
    def __init__(self, sweeps: List[dict]):
        self.sweeps = sweeps

    def as_table(self) -> Table:
        table = Table(
            "id", "status", "framework", "cloud_compute", "n_trials", show_header=True, header_style="bold green"
        )

        for sweep in self.sweeps:
            table.add_row(
                sweep["sweep_id"],
                sweep["status"],
                sweep["framework"],
                sweep["cloud_compute"],
                str(sweep["n_trials"]),
            )
        return table


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
        "exception",
        "best_model_path",
        title="Trials",
        show_header=True,
        header_style="bold green",
    )

    for idx, trial in sweep.trials.items():
        table.add_row(
            str(idx),
            str(trial.status),
            str(trial.best_model_score),
            str(trial.params.params),
            str(trial.monitor),
            str(trial.exception),
            str(trial.best_model_path),
        )
    console = Console()
    console.print(table)


class ShowSweepsCommand(ClientCommand):
    def run(self) -> None:
        # 1. Parse the user arguments.
        parser = argparse.ArgumentParser()
        parser.add_argument("--sweep_id", type=str, default=None, help="Provide the `sweep_id` to be showed.")
        hparams = parser.parse_args()

        # 2: Collect the SweepConfig
        resp = self.invoke_handler()

        # 3: Display the Sweeps or Sweep
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
