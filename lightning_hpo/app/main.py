import os
from uuid import uuid4

from lightning import LightningFlow
from lightning.app.components.database import Database, DatabaseClient
from lightning.app.frontend import StaticWebFrontend
from lightning.app.storage import Drive

from lightning_hpo.commands.artifacts.download import (
    _collect_artifact_urls,
    DownloadArtifactsCommand,
    DownloadArtifactsConfig,
    DownloadArtifactsConfigResponse,
)
from lightning_hpo.commands.artifacts.show import (
    _collect_artifact_paths,
    ShowArtifactsCommand,
    ShowArtifactsConfig,
    ShowArtifactsConfigResponse,
)
from lightning_hpo.commands.drive.create import CreateDriveCommand, DriveConfig
from lightning_hpo.commands.drive.delete import DeleteDriveCommand, DeleteDriveConfig
from lightning_hpo.commands.drive.show import ShowDriveCommand

# from lightning_hpo.controllers.notebook import NotebookController
from lightning_hpo.controllers.sweep import SweepController
from lightning_hpo.controllers.tensorboard import TensorboardController


class ResearchStudio(LightningFlow):
    def __init__(self):
        super().__init__()
        # 1: Create Drive
        self.drive = Drive("lit://uploaded_files")

        # 2: Controllers
        self.sweep_controller = SweepController(self.drive)
        # self.notebook_controller = NotebookController()
        self.tensorboard_controller = TensorboardController()

        # 4: Create the database.
        self.db = Database(
            models=[
                self.sweep_controller.model,
                # self.notebook_controller.model,
                self.tensorboard_controller.model,
                DriveConfig,
            ]
        )

        self.ready = False
        self._db_client = None
        self._token = uuid4().hex

    def run(self):
        self.db.run(token=self._token)

        if not self.db.alive():
            return

        if not self.ready:
            print("The Research Studio App is ready !")
            self.ready = True

        # 3: Run the controllers
        self.sweep_controller.run(self.db.db_url, token=self._token)
        # self.notebook_controller.run(self.db.db_url)
        self.tensorboard_controller.run(self.db.db_url, token=self._token)

    def configure_layout(self):
        return StaticWebFrontend(os.path.join(os.path.dirname(__file__), "ui", "build"))

    def show_artifacts(self, config: ShowArtifactsConfig) -> ShowArtifactsConfigResponse:
        sweeps = self.db_client.select_all(self.sweep_controller.model)
        return ShowArtifactsConfigResponse(
            sweep_names=[sweep.sweep_id for sweep in sweeps],
            experiment_names=[exp.name for sweep in sweeps for exp in sweep.experiments.values()],
            paths=_collect_artifact_paths(config),
        )

    def download_artifacts(self, config: DownloadArtifactsConfig) -> DownloadArtifactsConfigResponse:
        sweeps = self.db_client.select_all(self.sweep_controller.model)
        paths, urls = _collect_artifact_urls(config)
        return DownloadArtifactsConfigResponse(
            sweep_names=[sweep.sweep_id for sweep in sweeps],
            experiment_names=[exp.name for sweep in sweeps for exp in sweep.experiments.values()],
            paths=paths,
            urls=urls,
        )

    def create_drive(self, config: DriveConfig):
        drives = self.db_client.select_all(DriveConfig)
        for drive in drives:
            if drive.name == config.name:
                return f"The drive `{config.name}` already exists."
        self.db_client.insert(config)
        return f"The drive `{config.name}` has been created."

    def delete_drive(self, config: DeleteDriveConfig):
        drives = self.db_client.select_all(DriveConfig)
        for drive in drives:
            if drive.name == config.name:
                self.db_client.delete(drive)
                return f"The drive `{config.name}` has been deleted."
        return f"The drive `{config.name}` doesn't exist."

    def show_drives(self):
        return self.db_client.select_all(DriveConfig)

    def configure_commands(self):
        controller_commands = self.sweep_controller.configure_commands()
        # controller_commands += self.notebook_controller.configure_commands()
        controller_commands += self.tensorboard_controller.configure_commands()
        controller_commands += [
            {"show artifacts": ShowArtifactsCommand(self.show_artifacts)},
            {"download artifacts": DownloadArtifactsCommand(self.download_artifacts)},
            {"create drive": CreateDriveCommand(self.create_drive)},
            {"delete drive": DeleteDriveCommand(self.delete_drive)},
            {"show drives": ShowDriveCommand(self.show_drives)},
        ]
        return controller_commands

    @property
    def db_client(self) -> DatabaseClient:
        if self._db_client is None:
            assert self.db_url is not None
            self._db_client = DatabaseClient(self.db.db_url, token=self._token, model=self.model)
        return self._db_client
