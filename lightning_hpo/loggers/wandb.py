import os
from typing import Optional

import wandb
import wandb.apis.reports as wb

from lightning import LightningFlow
from lightning_hpo.loggers.base import Logger

class WandB(Logger):

    def __init__(self):
        super().__init__()
        self._validate_auth()
        self._api = wandb.Api(api_key=os.environ.get("WANDB_API_KEY"))
        self.sweep_id: Optional[str] = None
        self.storage_id: Optional[str] = None
        self.report_url: Optional[str] = None

    def on_start(
        self,
        sweep_id: str,
        title: Optional[str] = None,
        desc: Optional[str] = None,
    ):
        self.sweep_id = sweep_id
        wandb.require("report-editing:v0")
        report = self._api.create_report(project=self.sweep_id)
        report.title = f"{self.sweep_id.title()} Report" if not title else title
        if desc:
            report.description = desc
        panel_grid = wb.PanelGrid()
        run_set = wb.RunSet()
        run_set.entity = os.environ.get("WANDB_ENTITY")
        run_set.project = self.sweep_id
        panel_grid.runsets = [run_set]
        coords = wb.ParallelCoordinatesPlot(
            columns=[
                wb.reports.PCColumn("batch_size"),
                wb.reports.PCColumn("epoch"),
                wb.reports.PCColumn("loss"),
            ]
        )
        panel_grid.panels = [coords]
        run_set.set_filters_with_python_expr(f'User == "{os.environ.get("WANDB_ENTITY")}"')
        report.blocks = [panel_grid]
        report.save()
        self.storage_id = report.id
        base_url = f"https://wandb.ai/{os.getenv('WANDB_ENTITY')}/{self.sweep_id}/reports/"
        self.report_url = base_url + f"{self.sweep_id}--{self.storage_id}"
        self.report = self._api.load_report(self.report_url)
        return self.storage_id

    def on_trial_end(self, *_, **__):
        pass

    def on_batch_trial_end(self):
        panel_grid = wb.PanelGrid()
        run_set = wb.RunSet()
        run_set.entity = os.environ.get("WANDB_ENTITY")
        run_set.project = self.sweep_id
        panel_grid.runsets = [run_set]
        coords = wb.ParallelCoordinatesPlot(
            columns=[
                wb.reports.PCColumn("batch_size"),
                wb.reports.PCColumn("epoch"),
                wb.reports.PCColumn("loss"),
            ]
        )
        panel_grid.panels = [coords]
        run_set.set_filters_with_python_expr(f'User == "{os.environ.get("WANDB_ENTITY")}"')
        self.report.blocks = [panel_grid]

    @staticmethod
    def _validate_auth():
        if os.getenv("WANDB_API_KEY") is None or os.getenv("WANDB_ENTITY") is None:
            raise Exception(
                "You are trying to use wandb without setting your API key or entity. "
                "HINT: lightning run app app_name.py --env LOGGER=wandb --env WANDB_API_KEY=YOUR_API_KEY",
            )

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