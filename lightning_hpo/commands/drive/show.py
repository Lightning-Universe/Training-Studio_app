from lightning.app.utilities.commands import ClientCommand
from rich.console import Console
from rich.table import Table


class ShowDriveCommand(ClientCommand):

    description = "Show Drives."

    def run(self) -> None:
        response = self.invoke_handler()

        table = Table(
            "name",
            "source",
            "mount_path",
            title="Drives",
            show_header=True,
            header_style="bold green",
        )

        for drive in response:
            table.add_row(
                drive["name"],
                drive["source"],
                drive["mount_path"],
            )
        console = Console()
        console.print(table)
