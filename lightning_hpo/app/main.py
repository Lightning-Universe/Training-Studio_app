import os

from lightning import LightningFlow
from lightning.app.frontend import StaticWebFrontend
from lightning.app.storage import Drive

from lightning_hpo.commands.artefacts.download import (
    _collect_artefact_urls,
    DownloadArtefactsCommand,
    DownloadArtefactsConfig,
)
from lightning_hpo.commands.artefacts.show import _collect_artefact_paths, ShowArtefactsCommand, ShowArtefactsConfig
from lightning_hpo.components.servers.db import Database, DatabaseViz, FlowDatabase
from lightning_hpo.components.servers.file_server import FileServer
from lightning_hpo.controllers.notebook import NotebookController
from lightning_hpo.controllers.sweep import SweepController
from lightning_hpo.controllers.tensorboard import TensorboardController


class MainFlow(LightningFlow):
    def __init__(self, debug: bool = False, work_db: bool = False):
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
        db_cls = Database if work_db else FlowDatabase
        self.db = db_cls(
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
        # TODO: Remove them to reduce cost
        # 1: Start the servers.
        self.file_server.run()

        self.db.run()

        if self.debug:
            self.db_viz.run()

        # 2: Wait for the servers to be alive
        if not (self.file_server.alive() and self.db.alive()):
            return

        if not self.ready:
            print(f"The Training Studio App is ready ! Database URL: {self.db.db_url}")
            self.ready = True

        # 3: Run the controllers
        self.sweep_controller.run(self.db.db_url)
        self.notebook_controller.run(self.db.db_url)
        self.tensorboard_controller.run(self.db.db_url)

    def configure_layout(self):
        return StaticWebFrontend(os.path.join(os.path.dirname(__file__), "ui", "build"))

    def show_artefacts(self, config: ShowArtefactsConfig):
        return _collect_artefact_paths(config)

    def download_artefacts(self, config: DownloadArtefactsConfig):
        return _collect_artefact_urls(config)

    def configure_commands(self):
        controller_commands = self.sweep_controller.configure_commands()
        controller_commands += self.notebook_controller.configure_commands()
        controller_commands += self.tensorboard_controller.configure_commands()
        controller_commands += [
            {"show artefacts": ShowArtefactsCommand(self.show_artefacts)},
            {"download artefacts": DownloadArtefactsCommand(self.download_artefacts)},
        ]
        return controller_commands
