import os
from uuid import uuid4

from lightning import CloudCompute, LightningFlow
from lightning.app.components.database import Database, DatabaseClient
from lightning.app.frontend import StaticWebFrontend
from lightning.app.storage import Drive

from lightning_training_studio.commands.artifacts.download import (
    _collect_artifact_urls,
    DownloadArtifactsCommand,
    DownloadArtifactsConfig,
    DownloadArtifactsConfigResponse,
)
from lightning_training_studio.commands.artifacts.show import (
    _collect_artifact_paths,
    ShowArtifactsCommand,
    ShowArtifactsConfig,
    ShowArtifactsConfigResponse,
)
from lightning_training_studio.commands.data.create import CreateDataCommand, DataConfig
from lightning_training_studio.commands.data.delete import DeleteDataCommand, DeleteDataConfig
from lightning_training_studio.commands.data.show import ShowDataCommand
from lightning_training_studio.commands.logs.show import ShowLogsCommand

# from lightning_training_studio.controllers.notebook import NotebookController
from lightning_training_studio.controllers.sweep import SweepController
from lightning_training_studio.controllers.tensorboard import TensorboardController


class TrainingStudio(LightningFlow):
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
                DataConfig,
            ]
        )
        self.db.cloud_compute = CloudCompute("cpu", disk_size=80)

        self.has_setup = False
        self._db_client = None
        self._token = uuid4().hex
        self.seconds = ",".join([str(v) for v in range(0, 60, 1)])

    @property
    def ready(self) -> bool:
        return self.db.alive()

    def run(self):
        self.db.run(token=self._token)

        if not self.db.alive():
            return

        if not self.has_setup:
            print("The Training Studio App is ready !")
            self.has_setup = True

        # Run every seconds.
        if self.schedule(f"* * * * * {self.seconds}"):

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

    def create_data(self, config: DataConfig):
        drives = self.db_client.select_all(DataConfig)
        for drive in drives:
            if drive.name == config.name:
                return f"The data `{config.name}` already exists."
        self.db_client.insert(config)
        return f"The data `{config.name}` has been created."

    def delete_data(self, config: DeleteDataConfig):
        drives = self.db_client.select_all(DataConfig)
        for drive in drives:
            if drive.name == config.name:
                self.db_client.delete(drive)
                return f"The data `{config.name}` has been deleted."
        return f"The data `{config.name}` doesn't exist."

    def show_data(self):
        if self.db.db_url:
            return self.db_client.select_all(DataConfig)
        return []

    def configure_commands(self):
        controller_commands = self.sweep_controller.configure_commands()
        # controller_commands += self.notebook_controller.configure_commands()
        controller_commands += [
            {"show artifacts": ShowArtifactsCommand(self.show_artifacts)},
            {"download artifacts": DownloadArtifactsCommand(self.download_artifacts)},
            {"create data": CreateDataCommand(self.create_data)},
            {"delete data": DeleteDataCommand(self.delete_data)},
            {"show data": ShowDataCommand(self.show_data)},
            {"show logs": ShowLogsCommand(self.sweep_controller.show_logs)},
        ]
        return controller_commands

    def configure_api(self):
        return self.tensorboard_controller.configure_api()

    @property
    def db_client(self) -> DatabaseClient:
        if self._db_client is None:
            assert self.db.db_url is not None
            self._db_client = DatabaseClient(self.db.db_url, token=self._token)
        return self._db_client
