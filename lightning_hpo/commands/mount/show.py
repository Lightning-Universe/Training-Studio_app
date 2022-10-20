from lightning.app.utilities.commands import ClientCommand
from rich.console import Console
from rich.table import Table


class ShowMountCommand(ClientCommand):

    DESCRIPTION = "Show Mounts."

    def run(self) -> None:
        response = self.invoke_handler()

        table = Table(
            "name",
            "source",
            "mount_path",
            title="Mounts",
            show_header=True,
            header_style="bold green",
        )

        for mount in response:
            table.add_row(
                mount["name"],
                mount["source"],
                mount["mount_path"],
            )
        console = Console()
        console.print(table)
