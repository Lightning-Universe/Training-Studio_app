import os
import sys
import wandb

import wandb.apis.reports as wb


def main():

    api = wandb.Api(api_key=os.environ.get("WANDB_API_KEY"))

    project_name = "046eab8e"

    projectdir = os.path.join(os.getcwd(), project_name)

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
    run_set.set_filters_with_python_expr(f'User == "{os.environ.get("WANDB_ENTITY")}"')
    report.blocks = [panel_grid]
    report.save()
    print(report.id)


if __name__ == "__main__":
    os.environ["WANDB_ENTITY"] = sys.argv[1]
    os.environ["WANDB_API_KEY"] = sys.argv[2]
    main()
