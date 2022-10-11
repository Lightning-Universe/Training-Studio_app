import os
from argparse import ArgumentParser
from getpass import getuser
from pathlib import Path
from uuid import uuid4

from lightning.app.core.constants import APP_SERVER_HOST, APP_SERVER_PORT
from lightning.app.utilities.commands import ClientCommand

from lightning_hpo.commands.sweep.run import CustomLocalSourceCodeDir, ExperimentConfig, SweepConfig


class RunExperimentCommand(ClientCommand):

    DESCRIPTION = "Command to run an experiment."

    def run(self) -> None:
        parser = ArgumentParser()

        parser.add_argument("script_path", type=str, help="The path to the script to run.")
        parser.add_argument(
            "--requirements",
            default=",",
            type=lambda s: [v.replace(" ", "") for v in s.split(",")] if "," in s else s,
            help="List of requirements separated by a comma or requirements.txt filepath.",
        )
        parser.add_argument(
            "--cloud_compute",
            default="cpu",
            choices=["cpu", "cpu-small", "cpu-medium", "gpu", "gpu-fast", "gpu-fast-multi"],
            type=str,
            help="The machine to use in the cloud.",
        )
        parser.add_argument("--name", default=None, type=str, help="The name of the experiment.")
        parser.add_argument(
            "--logger",
            default="tensorboard",
            choices=["tensorboard", "wandb"],
            type=str,
            help="The logger to use with your sweep.",
        )
        parser.add_argument(
            "--num_nodes",
            default=1,
            type=int,
            help="The number of nodes.",
        )
        parser.add_argument(
            "--disk_size",
            default=10,
            type=int,
            help="The disk size in Gigabytes.",
        )
        parser.add_argument(
            "--drives", nargs="+", default=[], help="Provide a list of drives to add to yhe experiments."
        )
        hparams, args = parser.parse_known_args()

        id = str(uuid4()).split("-")[0]
        sweep_id = f"{getuser()}-{id}"

        if not os.path.exists(hparams.script_path):
            raise ValueError(f"The provided script doesn't exist: {hparams.script_path}")

        if isinstance(hparams.requirements, str) and os.path.exists(hparams.requirements):
            with open(hparams.requirements, "r") as f:
                hparams.requirements = [line.replace("\n", "") for line in f.readlines()]

        repo = CustomLocalSourceCodeDir(path=Path(hparams.script_path).parent.resolve())

        URL = self.state._state["vars"]["_layout"]["target"].replace("/root", "")
        if "localhost" in URL:
            URL = f"{APP_SERVER_HOST}:{APP_SERVER_PORT}"
        repo.package()
        repo.upload(url=f"{URL}/api/v1/upload_file/{sweep_id}")

        config = SweepConfig(
            sweep_id=sweep_id,
            script_path=hparams.script_path,
            total_experiments=1,
            parallel_experiments=1,
            requirements=hparams.requirements,
            script_args=args,
            distributions={},
            algorithm="",
            framework="pytorch_lightning",
            cloud_compute=hparams.cloud_compute,
            num_nodes=hparams.num_nodes,
            logger=hparams.logger,
            direction="minimize",  # This won't be used
            experiments={0: ExperimentConfig(name=hparams.name or str(uuid4()).split("-")[-1][:7], params={})},
            disk_size=hparams.disk_size,
            drive_names=hparams.drives,
        )
        response = self.invoke_handler(config=config)
        print(response)
