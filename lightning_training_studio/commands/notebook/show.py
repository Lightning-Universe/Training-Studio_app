from typing import List

from lightning.app.utilities.commands import ClientCommand
from rich.console import Console
from rich.table import Table

from lightning_training_studio.commands.notebook.run import NotebookConfig


def _show_notebooks(notebooks: List[NotebookConfig]):
    table = Table(
        "name",
        "status",
        "cloud_compute",
        "requirements",
        title="Notebooks",
        show_header=True,
        header_style="bold green",
    )

    for notebook in notebooks:
        table.add_row(
            notebook.notebook_name,
            notebook.stage,
            notebook.cloud_compute,
            str(notebook.requirements),
        )
    console = Console()
    console.print(table)


class ShowNotebookCommand(ClientCommand):
    def run(self) -> None:
        response = self.invoke_handler()
        _show_notebooks([NotebookConfig(**notebook) for notebook in response])
