from pydantic import BaseModel
from typing import List, Any, Optional
from lightning.app.utilities.commands import ClientCommand
from lightning_app.source_code import LocalSourceCodeDir
from uuid import uuid4
from pathlib import Path


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


class SweepCommand(ClientCommand):

    def run(
        self,
        script_path: str,
        n_trials: str,
        simultaneous_trials: Optional[str] = None,
        requirements: Optional[List[str]] = None,
        script_args: Optional[List[str]] = None,
        framework: Optional[str] = None,
        cloud_compute: Optional["str"] = "default",
    ) -> None:
        sweep_id = f"sweep-{str(uuid4())}"
        repo = LocalSourceCodeDir(path=Path(script_path).parent.resolve())
        url = self.state.file_server._state["vars"]["_url"]
        repo.package()
        repo.upload(url=f"{url}/uploadfile/{sweep_id}")
        simultaneous_trials = int(simultaneous_trials) if isinstance(simultaneous_trials, str) else 1
        distributions = []
        self.invoke_handler(config=SweepConfig(
            sweep_id=sweep_id,
            script_path=script_path,
            n_trials=int(n_trials),
            simultaneous_trials=simultaneous_trials,
            requirements = requirements or [],
            script_args = script_args or [],
            distributions=distributions,
            framework=framework or "pytorch_lightning",
            cloud_compute=cloud_compute,
            code=True,
        ))