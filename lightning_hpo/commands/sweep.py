from pydantic import BaseModel
from typing import List, Any, Optional
from lightning_app.utilities.commands import ClientCommand
from uuid import uuid4


class SweepConfig(BaseModel):
    sweep_id: Optional[str] = None
    upload_url = str
    script_path: str
    n_trials: int
    simultaneous_trials: int
    requirements: List[str]
    script_args: List[str]
    distributions: Any
    framework: str
    cloud_compute: Any


class SweepCommand(ClientCommand):

    def run(self, script_path: str, **kwargs) -> None:
        SweepConfig(
            sweep_id = str(uuid4()),
            script_path=script_path,
        )