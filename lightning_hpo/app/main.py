from lightning import LightningFlow
from lightning.app.storage import Drive

from lightning_hpo.commands.notebook import NotebookConfig
from lightning_hpo.commands.sweep.run_sweep import SweepConfig
from lightning_hpo.components.servers.db.server import Database
from lightning_hpo.components.servers.db.visualization import DatabaseViz
from lightning_hpo.components.servers.file_server import FileServer
from lightning_hpo.controllers.notebook import NotebookController
from lightning_hpo.controllers.sweeper import SweepController


class MainFlow(LightningFlow):
    def __init__(self):
        super().__init__()
        # 1: General managers
        self.drive = Drive("lit://code")
        self.file_server = FileServer(self.drive)
        self.db = Database(models=[SweepConfig, NotebookConfig])
        self.db_viz = DatabaseViz()

        # 2: Controllers
        self.sweep_controller = SweepController(self.drive)
        self.notebook_controller = NotebookController()

    def run(self):
        # 1: Start the servers.
        self.file_server.run()
        self.db.run()
        self.db_viz.run()

        # 2: Wait for the servers to be alive
        if not (self.file_server.alive() and self.db.alive()):
            return

        # 3: Run the controllers
        self.sweep_controller.run(self.db.url)
        self.notebook_controller.run(self.db.url)

    def configure_layout(self):
        tabs = [{"name": "Dashboard", "content": self.sweep_controller}]
        tabs += [{"name": "Database Viz", "content": self.db_viz}]
        for sweep in self.sweep_controller.sweeps.values():
            if sweep.show:
                tabs += sweep.configure_layout()
        return tabs

    def configure_commands(self):
        return self.sweep_controller.configure_commands() + self.notebook_controller.configure_commands()
