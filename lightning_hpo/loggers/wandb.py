import os
from typing import Optional, Dict, Any

from lightning import LightningFlow
from lightning_hpo.loggers.base import Logger

class WandB(Logger):

    def __init__(self):
        super().__init__()
        import wandb

        self._validate_auth()
        os.environ["WANDB_REQUIRE_REPORT_EDITING_V0"] = "1"
        self._api = wandb.Api(api_key=os.environ.get("WANDB_API_KEY"))
        self.entity = os.getenv('WANDB_ENTITY')
        self.sweep_id: Optional[str] = None
        self.storage_id: Optional[str] = None
        self.report_url: Optional[str] = None
        self.report = None

    def on_trial_start(
        self,
        sweep_id: str,
        trial_id: int,
        params: Dict[str, Any],
        title: Optional[str] = None,
        desc: Optional[str] = None,
    ):

        import wandb
        from wandb.apis import reports

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
        self.report_url = f"https://wandb.ai/{self.entity}/{self.sweep_id}/reports/{self.sweep_id}--{self.report.id}"
        self.report = self._api.load_report(self.report_url)
        panel_grid = reports.PanelGrid()
        run_set = reports.RunSet()
        run_set.entity = self.entity
        run_set.project = self.sweep_id
        panel_grid.runsets = [run_set]
        keys = list(params.keys()) + ["score"]
        columns = [reports.PCColumn(p) for p in keys]
        coords = reports.ParallelCoordinatesPlot(columns)
        coords.entity = self.entity
        coords.project = self.sweep_id
        panel_grid.panels = [coords]
        run_set.set_filters_with_python_expr(f'User == "{self.entity}"')
        self.report.blocks = [panel_grid]
        self.report.save()

    def on_trial_end(self, score, params):
        pass

    def connect(self, flow: LightningFlow):
        pass

    def configure_layout(self):
        if self.storage_id is not None:
            reports = f"https://wandb.ai/{os.getenv('WANDB_ENTITY')}/{self.sweep_id}/reports/{self.sweep_id}"
            tab1 = {"name": "Project", "content": reports}
            sweep_report = f"https://wandb.ai/{os.getenv('WANDB_ENTITY')}/{self.sweep_id}/reports/{self.sweep_id}--{self.storage_id}"  # noqa: E501
            tab2 = {"name": "Report", "content": sweep_report}
            content = [tab1, tab2]
        else:
            reports = f"https://wandb.ai/{os.getenv('WANDB_ENTITY')}/{self.sweep_id}/reports/{self.sweep_id}"
            tab1 = {"name": "Project", "content": reports}
            content = [tab1]
        return content

    def configure_tracer(self, tracer, params: Dict[str, Any], trial_id: int):
        from pytorch_lightning import Trainer
        from pytorch_lightning.loggers import WandbLogger

        import wandb

        wandb.init(
            project=self.sweep_id,
            entity=os.getenv("WANDB_ENTITY"),
            name=f"trial_{trial_id}",
            config=params,
        )

        def trainer_pre_fn(trainer, *args, **kwargs):
            logger = WandbLogger(
                save_dir=os.path.join(os.getcwd(), os.environ.get("LOGS_DIR")),
                project=self.sweep_id,
                entity=os.getenv("WANDB_ENTITY"),
                name=f"trial_{trial_id}",
            )
            kwargs["logger"] = [logger]
            return {}, args, kwargs

        tracer.add_traced(Trainer, "__init__", trainer_pre_fn)

    @staticmethod
    def _validate_auth():
        if os.getenv("WANDB_API_KEY") is None or os.getenv("WANDB_ENTITY") is None:
            raise Exception(
                "You are trying to use wandb without setting your API key or entity. "
                "HINT: lightning run app app_name.py --env LOGGER=wandb --env WANDB_API_KEY=YOUR_API_KEY",
            )