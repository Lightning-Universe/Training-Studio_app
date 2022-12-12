import argparse
import sys
from typing import List

from lightning.app.cli.commands.connection import _retrieve_connection_to_an_app
from lightning.app.cli.commands.logs import _show_logs
from lightning.app.utilities.commands import ClientCommand
from pydantic import BaseModel


class ShowLogsConfig(BaseModel):
    name: str
    components: List[str]


class ShowLogsCommand(ClientCommand):

    description: str = "Show logs of an experiment or a sweep. Optionally follow logs as they stream."

    def run(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--names",
            nargs="+",
            default=[],
            help="The name or names of the Experiment(s), Sweep(s) or components to show logs from.",
        )
        parser.add_argument("-f", "--follow", action="store_true", default=False)
        hparams = parser.parse_args()

        logs_config: List[ShowLogsConfig] = self.invoke_handler()

        components = []
        sweeps = [c["name"] for c in logs_config if len(c["components"]) > 1]
        experiments = [c["name"] for c in logs_config if len(c["components"]) == 1]

        if not hparams.names:
            for config in logs_config:
                components.extend(config["components"])
        else:
            for config in logs_config:
                for name in hparams.names:
                    if name == config["name"]:
                        components.extend(config["components"])

        if not components:
            if not sweeps and not experiments:
                print("There isn't logs yet as you haven't run any experiments or sweeps.")
            else:
                print(
                    f"The provided name {hparams.names} wasn't found."
                    f" Here are the sweeps {sweeps} and experiments {experiments}."
                )
            sys.exit(0)

        app_name, _ = _retrieve_connection_to_an_app()

        if app_name == "localhost":
            print("The command `show logs` is currently supported only in the cloud.")
            sys.exit(0)

        _show_logs(app_name, list(set(components)), hparams.follow)
