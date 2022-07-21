import os
import lightning as L
from lightning_hpo.config import BaseConfig

import wandb
import wandb.apis.reports as wb


class WandbConfig(BaseConfig):
    def __init__(self):
        super().__init__()

    def create_wandb_report(self):
        api = wandb.Api(api_key=os.environ.get("WANDB_API_KEY"))
        project_name = self.sweep_id
        wandb.require("report-editing:v0")
        report = api.create_report(project=project_name)
        report.title = "A fabulous title"
        report.description = "A descriptive description"
        panel_grid = wb.PanelGrid()
        run_set = wb.RunSet()
        run_set.entity = os.environ.get("WANDB_ENTITY")
        run_set.project = project_name
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
        self.wandb_storage_id = report.id
