from lightning import LightningFlow
from lightning.app.storage import Drive

from lightning_hpo.commands.artefacts.download import (
    _collect_artefact_urls,
    DownloadArtefactsCommand,
    DownloadArtefactsConfig,
)
from lightning_hpo.commands.artefacts.show import _collect_artefact_paths, ShowArtefactsCommand, ShowArtefactsConfig
from lightning_hpo.components.servers.db import Database, DatabaseViz
from lightning_hpo.components.servers.file_server import FileServer
from lightning_hpo.controllers.notebook import NotebookController
from lightning_hpo.controllers.sweep import SweepController
from lightning_hpo.controllers.tensorboard import TensorboardController
from lightning_hpo.utilities.enum import Status


class MainFlow(LightningFlow):
    def __init__(self, debug: bool = False):
        super().__init__()
        self.debug = debug

        # 1: Create Drive
        self.drive = Drive("lit://code")

        # 2: Controllers
        self.sweep_controller = SweepController(self.drive)
        self.notebook_controller = NotebookController()
        self.tensorboard_controller = TensorboardController()

        # 3: Create the File Server to upload code or data.
        self.file_server = FileServer(self.drive)

        # 4: Create the database.
        self.db = Database(
            models=[
                self.sweep_controller.model,
                self.notebook_controller.model,
                self.tensorboard_controller.model,
            ]
        )

        if self.debug:
            self.db_viz = DatabaseViz()

        self.ready = False

    def run(self):
        # 1: Start the servers.
        self.file_server.run()
        self.db.run()
        if self.debug:
            self.db_viz.run()

        # 2: Wait for the servers to be alive
        if not (self.file_server.alive() and self.db.alive()):
            return

        if not self.ready:
            print(f"The Training App is ready ! Database URL: {self.db.db_url}")
            self.ready = True

        # 3: Run the controllers
        self.sweep_controller.run(self.db.db_url)
        self.notebook_controller.run(self.db.db_url)
        self.tensorboard_controller.run(self.db.db_url)

    def configure_layout(self):
        tabs = [{"name": "Dashboard", "content": self.sweep_controller}]
        if self.debug:
            tabs += [{"name": "Database Viz", "content": self.db_viz}]
        for sweep in self.sweep_controller.resources.values():
            if sweep.show:
                tabs += sweep.configure_layout()

        for sweep_id, tensorboard in self.tensorboard_controller.resources.items():
            tabs += [{"name": f"tensorboard_{sweep_id}", "content": tensorboard}]

        for notebook_name, notebook in self.notebook_controller.resources.items():
            if notebook._config.desired_state == Status.RUNNING:
                tabs += [{"name": notebook_name, "content": notebook}]
        return tabs

    def show_artefacts(self, config: ShowArtefactsConfig):
        return _collect_artefact_paths(config)

    def download_artefacts(self, config: DownloadArtefactsConfig):
        return _collect_artefact_urls(config)

    def configure_commands(self):
        controller_commands = self.sweep_controller.configure_commands()
        controller_commands += self.notebook_controller.configure_commands()
        controller_commands += [
            {"show artefacts": ShowArtefactsCommand(self.show_artefacts)},
            {"download artefacts": DownloadArtefactsCommand(self.download_artefacts)},
        ]
        return controller_commands
