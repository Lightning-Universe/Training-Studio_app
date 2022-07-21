from pydantic import BaseModel
from typing import List, Any, Dict
from lightning.app.utilities.commands import ClientCommand
from lightning_app.source_code import LocalSourceCodeDir
from uuid import uuid4
from pathlib import Path
from argparse import ArgumentParser
import sys
import re
import os


class SweepConfig(BaseModel):
    sweep_id: str
    script_path: str
    n_trials: int
    simultaneous_trials: int
    requirements: List[str]
    script_args: List[str]
    distributions: Any
    framework: str
    cloud_compute: Any
    code: bool


class DistributionParser:

    @staticmethod
    def is_distribution(argument: str) -> bool:
        ...

    @staticmethod
    def parse(argument: str) -> Dict:
        ...


class UniformDistributionParser(DistributionParser):

    @staticmethod
    def is_distribution(argument: str) -> bool:
        return "uniform" in argument

    @staticmethod
    def parse(argument: str):
        name, value = argument.split("=")
        regex = "[0-9]*\.[0-9]*"
        low, high = re.findall(regex, value)
        return {
            name: {
                "distribution": "uniform",
                "low": float(low),
                "high": float(high)
            }
        }

class LogUniformDistributionParser(DistributionParser):

    @staticmethod
    def is_distribution(argument: str) -> bool:
        return "log_uniform" in argument

    @staticmethod
    def parse(argument: str):
        name, value = argument.split("=")
        regex = "[0-9]*\.[0-9]*"
        low, high = re.findall(regex, value)
        return {
            name: {
                "distribution": "log_uniform",
                "low": float(low),
                "high": float(high)
            }
        }

class CategoricalDistributionParser(DistributionParser):

    @staticmethod
    def is_distribution(argument: str) -> bool:
        return "categorical" in argument

    @staticmethod
    def parse(argument: str):
        name, value = argument.split("=")
        choices = value.split('[')[1].split("]")[0].split(", ")
        return {
            name: {
                "distribution": "categorical",
                "choices": choices,
            }
        }

class SweepCommand(ClientCommand):

    SUPPORTED_DISTRIBUTIONS = ("uniform", "log_uniform", "categorical")

    def run(self) -> None:
        script_path = sys.argv[0]

        parser = ArgumentParser()
        parser.add_argument('--n_trials', type=int, help="Number of trials to run.")
        parser.add_argument('--simultaneous_trials', default=1, type=int, help="Number of trials to run.")
        parser.add_argument('--requirements', nargs='+', default=[], help="Requirements file.")
        parser.add_argument('--framework', default="pytorch_lightning", type=str, help="The framework you are using.")
        parser.add_argument('--cloud_compute', default="cpu", type=str, help="The machine to use in the cloud.")
        parser.add_argument('--sweep_id', default=None, type=str, help="The sweep you want to run upon.")
        hparams, args = parser.parse_known_args()

        if any("=" not in arg for arg in args):
            raise Exception("Please, provide the arguments as follows --x=y")

        script_args = []
        distributions = {}
        for arg in args:
            arg = arg.replace("--", "")
            is_distribution = False
            for p in [UniformDistributionParser, LogUniformDistributionParser, CategoricalDistributionParser]:
                if p.is_distribution(arg):
                    distributions.update(p.parse(arg))
                    is_distribution = True
                    break
            if not is_distribution:
                script_args.append(arg)

        sweep_id = hparams.sweep_id or f"sweep-{str(uuid4())}"

        if not os.path.exists(script_path):
            raise Exception("The provided script doesn't exists.")


        repo = LocalSourceCodeDir(path=Path(script_path).parent.resolve())
        url = self.state.file_server._state["vars"]["_url"]
        repo.package()
        repo.upload(url=f"{url}/uploadfile/{sweep_id}")
        self.invoke_handler(config=SweepConfig(
            sweep_id=sweep_id,
            script_path=script_path,
            n_trials=int(hparams.n_trials),
            simultaneous_trials=hparams.simultaneous_trials,
            requirements=hparams.requirements,
            script_args=script_args,
            distributions=distributions,
            framework=hparams.framework,
            cloud_compute=hparams.cloud_compute,
            code=True,
        ))
        print(f"Launched a sweep {sweep_id}")