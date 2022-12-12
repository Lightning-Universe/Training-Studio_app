import os
from typing import Any, Dict, Optional

from lightning import LightningFlow

from lightning_training_studio.loggers.logger import Logger
from lightning_training_studio.utilities.imports import _IS_PYTORCH_LIGHTNING_AVAILABLE, _IS_WANDB_AVAILABLE

if _IS_PYTORCH_LIGHTNING_AVAILABLE:
    import pytorch_lightning
else:
    import lightning.pytorch as pytorch_lightning

if _IS_WANDB_AVAILABLE:
    import wandb


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

    def on_after_experiment_start(
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

    def on_after_experiment_end(
        self, sweep_id: str, experiment_id: int, monitor: str, score: float, params: Dict[str, Any]
    ):
        if getattr(self.report, "blocks"):
            return

        panel_grid = wandb.apis.reports.PanelGrid()
        run_set = wandb.apis.reports.RunSet()
        run_set.entity = self.entity
        run_set.project = self.sweep_id
        panel_grid.runsets = [run_set]
        keys = list(params.keys()) + [monitor]
        coords = wandb.apis.reports.ParallelCoordinatesPlot([wandb.apis.reports.PCColumn(p) for p in keys])
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

    def configure_tracer(self, tracer, sweep_id: str, experiment_id: int, experiment_name: str, params: Dict[str, Any]):
        wandb.init(
            project=sweep_id,
            entity=self.entity,
            name=f"experiment_{experiment_id}",
            config=params,
        )

        for k, v in params.items():
            wandb.summary[k] = v

        def trainer_pre_fn(trainer, *args, **kwargs):
            logger = pytorch_lightning.loggers.WandbLogger(
                save_dir=os.path.join(os.getcwd(), "wandb/lightning_logs"),
                project=sweep_id,
                entity=self.entity,
                name=f"experiment_{experiment_id}",
            )
            kwargs["logger"] = [logger]
            return {}, args, kwargs

        tracer.add_traced(pytorch_lightning.Trainer, "__init__", pre_fn=trainer_pre_fn)

    def get_url(self, experiment_id: int) -> None:
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
