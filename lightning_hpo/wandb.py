import os
from typing import Optional
import lightning as L
from lightning_hpo.config import BaseConfig

import wandb
import wandb.apis.reports as wb

STORAGE_ID = str


class WandB(BaseConfig):
    def __init__(self):
        super().__init__()
        self._api = wandb.Api(api_key=os.environ.get("WANDB_API_KEY"))
        self.sweep_id: Optional[str] = None
        self.storage_id: Optional[str] = None
        self.report_url: Optional[str] = None

    def create_report(
        self,
        sweep_id: str,
        title: Optional[str] = None,
        desc: Optional[str] = None,
    ) -> STORAGE_ID:
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
        run_set.set_filters_with_python_expr(
            f'User == "{os.environ.get("WANDB_ENTITY")}"'
        )
        report.blocks = [panel_grid]
        report.save()
        self.storage_id = report.id
        base_url = (
            f"https://wandb.ai/{os.getenv('WANDB_ENTITY')}/{self.sweep_id}/reports/"
        )
        self.report_url = base_url + f"{self.sweep_id}--{self.storage_id}"
        self.report = self._api.load_report(self.report_url)
        return self.storage_id

    def update_report(self):
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
        run_set.set_filters_with_python_expr(
            f'User == "{os.environ.get("WANDB_ENTITY")}"'
        )
        self.report.blocks = [panel_grid]
