import os
from typing import Any, Dict, Optional

import wandb
from lightning import LightningFlow

from lightning_hpo.loggers.logger import Logger


class WandbLogger(Logger):
    def __init__(self):
        super().__init__()
        self._validate_auth()
        os.environ["WANDB_REQUIRE_REPORT_EDITING_V0"] = "1"
        self._api = wandb.Api(api_key=os.environ.get("WANDB_API_KEY"))
        self.entity = os.getenv("WANDB_ENTITY")
        self.sweep_id: Optional[str] = None
        self.storage_id: Optional[str] = None
        self.report_url: Optional[str] = None
        self.report = None

    def on_after_trial_start(
        self,
        sweep_id: str,
        title: Optional[str] = None,
        desc: Optional[str] = None,
    ):

        from wandb.apis import reports  # noqa F401

        if self.sweep_id:
            return

        self.sweep_id = sweep_id
        wandb.require("report-editing:v0")
        self.report = self._api.create_report(project=self.sweep_id)
        self.report.title = f"{self.sweep_id.title()} Report" if not title else title
        if desc:
            self.report.description = desc

        self.report.save()
        self.storage_id = self.report.id
        self.report_url = f"https://wandb.ai/{self.entity}/{self.sweep_id}/reports/{self.sweep_id}--{self.report.id}"

    def on_after_trial_end(self, sweep_id: str, trial_id: int, monitor: str, score: float, params: Dict[str, Any]):
        from wandb.apis import reports

        if getattr(self.report, "blocks"):
            return

        panel_grid = reports.PanelGrid()
        run_set = reports.RunSet()
        run_set.entity = self.entity
        run_set.project = self.sweep_id
        panel_grid.runsets = [run_set]
        keys = list(params.keys()) + [monitor]
        coords = reports.ParallelCoordinatesPlot([reports.PCColumn(p) for p in keys])
        coords.layout = {"x": 0, "y": 0, "w": 24, "h": 10}
        coords.entity = self.entity
        coords.project = self.sweep_id
        panel_grid.panels = [coords]
        run_set.set_filters_with_python_expr(f'User == "{self.entity}"')
        self.report.blocks = [panel_grid]
        self.report.save()

    def connect(self, flow: LightningFlow):
        pass

    def configure_layout(self):
        reports = report = ""
        if self.storage_id is not None:
            reports = f"https://wandb.ai/{self.entity}/{self.sweep_id}/reports/{self.sweep_id}"
            report = f"https://wandb.ai/{self.entity}/{self.sweep_id}/reports/{self.sweep_id}--{self.storage_id}"  # noqa: E501
        return [{"name": "Project", "content": reports}, {"name": "Report", "content": report}]

    def configure_tracer(self, tracer, sweep_id: str, trial_id: int, params: Dict[str, Any]):
        import wandb
        from pytorch_lightning import Trainer
        from pytorch_lightning.loggers import WandbLogger

        wandb.init(
            project=sweep_id,
            entity=self.entity,
            name=f"trial_{trial_id}",
            config=params,
        )

        for k, v in params.items():
            wandb.summary[k] = v

        def trainer_pre_fn(trainer, *args, **kwargs):
            logger = WandbLogger(
                save_dir=os.path.join(os.getcwd(), "wandb/lightning_logs"),
                project=sweep_id,
                entity=self.entity,
                name=f"trial_{trial_id}",
            )
            kwargs["logger"] = [logger]
            return {}, args, kwargs

        tracer.add_traced(Trainer, "__init__", pre_fn=trainer_pre_fn)

    def get_url(self, trial_id: int) -> None:
        if self.storage_id is not None:
            return f"https://wandb.ai/{self.entity}/{self.sweep_id}/reports/{self.sweep_id}--{self.storage_id}"
        return f"https://wandb.ai/{self.entity}/{self.sweep_id}/reports/{self.sweep_id}"

    @staticmethod
    def _validate_auth():
        if os.getenv("WANDB_API_KEY") is None or os.getenv("WANDB_ENTITY") is None:
            raise Exception(
                "You are trying to use wandb without setting your API key or entity. "
                "HINT: lightning run app app.py --env WANDB_API_KEY=YOUR_API_KEY --env WANDB_ENTITY=YOUR_ENTITY",
            )
