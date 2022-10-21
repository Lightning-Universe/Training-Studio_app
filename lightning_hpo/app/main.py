import os

from lightning import LightningFlow
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
from lightning_hpo.commands.data.create import CreateDataCommand, DataConfig
from lightning_hpo.commands.data.delete import DeleteDataCommand, DeleteDataConfig
from lightning_hpo.commands.data.show import ShowDataCommand
from lightning_hpo.components.servers.db import (
    Database,
    DatabaseConnector,
    DatabaseViz,
    FlowDatabase,
    FlowDatabaseConnector,
)

# from lightning_hpo.controllers.notebook import NotebookController
from lightning_hpo.controllers.sweep import SweepController
from lightning_hpo.controllers.tensorboard import TensorboardController


class TrainingStudio(LightningFlow):
    def __init__(self, debug: bool = False, work_db: bool = True):
        super().__init__()
        self.debug = debug

        # 1: Create Drive
        self.drive = Drive("lit://uploaded_files")

        # 2: Controllers
        self.sweep_controller = SweepController(self.drive)
        # self.notebook_controller = NotebookController()
        self.tensorboard_controller = TensorboardController()

        # 4: Create the database.
        db_cls = Database if work_db else FlowDatabase
        self.db = db_cls(
            models=[
                self.sweep_controller.model,
                # self.notebook_controller.model,
                self.tensorboard_controller.model,
                DataConfig,
            ]
        )

        if self.debug:
            self.db_viz = DatabaseViz()

        self.ready = False
        self._client = None

    def run(self):
        self.db.run()

        if self.debug:
            self.db_viz.run()

        if not self.db.alive():
            return

        if not self.ready:
            print("The Research Studio App is ready !")
            self.ready = True

        # 3: Run the controllers
        self.sweep_controller.run(self.db.db_url)
        # self.notebook_controller.run(self.db.db_url)
        self.tensorboard_controller.run(self.db.db_url)

    def configure_layout(self):
        return StaticWebFrontend(os.path.join(os.path.dirname(__file__), "ui", "build"))

    def show_artifacts(self, config: ShowArtifactsConfig) -> ShowArtifactsConfigResponse:
        sweeps = self.db_client.get(self.sweep_controller.model)
        return ShowArtifactsConfigResponse(
            sweep_names=[sweep.sweep_id for sweep in sweeps],
            experiment_names=[exp.name for sweep in sweeps for exp in sweep.experiments.values()],
            paths=_collect_artifact_paths(config),
        )

    def download_artifacts(self, config: DownloadArtifactsConfig) -> DownloadArtifactsConfigResponse:
        sweeps = self.db_client.get(self.sweep_controller.model)
        paths, urls = _collect_artifact_urls(config)
        return DownloadArtifactsConfigResponse(
            sweep_names=[sweep.sweep_id for sweep in sweeps],
            experiment_names=[exp.name for sweep in sweeps for exp in sweep.experiments.values()],
            paths=paths,
            urls=urls,
        )

    def create_mount(self, config: DataConfig):
        mounts = self.db_client.get(DataConfig)
        for mount in mounts:
            if mount.name == config.name:
                return f"The mount `{config.name}` already exists."
        self.db_client.post(config)
        return f"The mount `{config.name}` has been created."

    def delete_mount(self, config: DeleteDataConfig):
        mounts = self.db_client.get(DataConfig)
        for mount in mounts:
            if mount.name == config.name:
                self.db_client.delete(mount)
                return f"The mount `{config.name}` has been deleted."
        return f"The mount `{config.name}` doesn't exist."

    def show_mounts(self):
        return self.db_client.get(DataConfig)

    def configure_commands(self):
        controller_commands = self.sweep_controller.configure_commands()
        # controller_commands += self.notebook_controller.configure_commands()
        controller_commands += self.tensorboard_controller.configure_commands()
        controller_commands += [
            {"show artifacts": ShowArtifactsCommand(self.show_artifacts)},
            {"download artifacts": DownloadArtifactsCommand(self.download_artifacts)},
            {"create data": CreateDataCommand(self.create_mount)},
            {"delete data": DeleteDataCommand(self.delete_mount)},
            {"show data": ShowDataCommand(self.show_mounts)},
        ]
        return controller_commands

    @property
    def db_client(self):
        if self._client is None:
            assert self.db.db_url is not None
            if self.db.db_url == "flow":
                self._client = FlowDatabaseConnector(None)
            else:
                self._client = DatabaseConnector(None, db_url=self.db.db_url + "/general/")
        return self._client
