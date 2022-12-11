import os
from argparse import ArgumentParser
from getpass import getuser
from pathlib import Path
from uuid import uuid4

from lightning.app.utilities.commands import ClientCommand

from lightning_training_studio.commands.sweep.run import CustomLocalSourceCodeDir, ExperimentConfig, SweepConfig


class RunExperimentCommand(ClientCommand):

    description = """Run an experiment by providing a script, the cloud compute type and optional
                     data entries to be made available at a given path."""

    def run(self) -> None:
        parser = ArgumentParser()

        parser.add_argument("script_path", type=str, help="The path to the script to run.")
        parser.add_argument(
            "--requirements",
            nargs="+",
            default=[],
            help="List of requirements separated by a comma or requirements.txt filepath.",
        )
        parser.add_argument(
            "--packages",
            nargs="+",
            default=[],
            help="List of system packages to be installed via apt install, separated by a comma.",
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
            default=80,
            type=int,
            help="The disk size in Gigabytes.",
        )
        parser.add_argument(
            "--data",
            nargs="+",
            default=[],
            help="Provide a list of Data (and optionally the mount_path in the format `<name>:<mount_path>`) to mount to the experiment.",
        )
        parser.add_argument(
            "--framework",
            default="pytorch_lightning",
            choices=["pytorch_lightning", "base"],
            type=str,
            help="Which framework you are using.",
        )
        parser.add_argument(
            "--pip-install-source",
            default=False,
            action="store_true",
            help="Run `pip install -e .` on the uploaded source before running",
        )

        hparams, args = parser.parse_known_args()

        name = hparams.name or str(uuid4()).split("-")[-1][:7]

        if not os.path.exists(hparams.script_path):
            raise FileNotFoundError(f"The provided script doesn't exist: {hparams.script_path}")

        if len(hparams.requirements) == 1 and Path(hparams.requirements[0]).resolve().exists():
            requirements_path = Path(hparams.requirements[0]).resolve()
            with open(requirements_path, "r") as f:
                hparams.requirements = [line.replace("\n", "") for line in f.readlines() if line.strip()]

        repo = CustomLocalSourceCodeDir(path=Path(hparams.script_path).parent.resolve())
        repo.package()
        repo.upload(url=f"{self.app_url}/api/v1/upload_file/{name}")

        data_split = [data.split(":") if ":" in data else (data, None) for data in hparams.data]
        data = {data[0]: data[1] for data in data_split}

        config = SweepConfig(
            sweep_id=name,
            script_path=hparams.script_path,
            total_experiments=1,
            parallel_experiments=1,
            requirements=hparams.requirements,
            packages=hparams.packages,
            script_args=args,
            distributions={},
            algorithm="",
            framework=hparams.framework,
            cloud_compute=hparams.cloud_compute,
            num_nodes=hparams.num_nodes,
            logger=hparams.logger,
            direction="minimize",  # This won't be used
            experiments={0: ExperimentConfig(name=name, params={})},
            disk_size=hparams.disk_size,
            pip_install_source=hparams.pip_install_source,
            data=data,
            username=str(getuser()),
        )
        response = self.invoke_handler(config=config)
        print(response)
