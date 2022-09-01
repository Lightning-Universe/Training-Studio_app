from lightning_hpo.components.servers.db.models import GeneralModel
from typing import List
from lightning.app.utilities.commands import ClientCommand
import requests
import abc
from rich.console import Console

from rich.table import Table


class Formatable(abc.ABC):
    @abc.abstractmethod
    def as_table(self) -> Table:
        pass


class SweepsList(Formatable):
    def __init__(self, sweeps: List[dict]):
        self.sweeps = sweeps

    def as_table(self) -> Table:
        # TODO: Improve the table format.
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


class ShowSweepsListCommand(ClientCommand):
    def run(self) -> None:
        # 1: Get the database URL
        db_url = self.invoke_handler()

        # 2: Get the sweeps from the database
        resp = requests.get(
            db_url + "/general/",
            data=GeneralModel(
                cls_name="SweepConfig", cls_module="lightning_hpo.commands.sweep.run_sweep", data=""
            ).json(),
        )
        sweeps = SweepsList(resp.json())
        console = Console()
        # 3: Print the sweeps
        console.print(sweeps.as_table())
