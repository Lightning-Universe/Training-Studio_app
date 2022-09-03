import argparse
import os
from pathlib import Path
from typing import List, Optional, Tuple, Union

import requests
from lightning.app.storage.copier import copy_files
from lightning.app.storage.path import shared_storage_path
from lightning.app.utilities.commands import ClientCommand
from lightning.app.utilities.network import LightningClient
from lightning_app.utilities.cloud import _get_project
from pydantic import BaseModel

from lightning_hpo.commands.artefacts.show import _collect_artefact_paths, _filter_paths, ShowArtefactsConfig


class DownloadArtefactsConfig(BaseModel):
    include: Optional[str] = None
    exclude: Optional[str] = None


class DownloadArtefactsCommand(ClientCommand):
    def run(self) -> None:
        # 1. Parse the user arguments.
        parser = argparse.ArgumentParser()
        parser.add_argument("output_dir", type=str, help="Provide the output directory for the artefacts..")
        parser.add_argument("--include", type=str, default=None, help="Provide a regex to include some specific files.")
        parser.add_argument("--exclude", type=str, default=None, help="Provide a regex to exclude some specific files.")
        parser.add_argument(
            "--overwrite", type=str, default=False, help="Whether to overwrite the artefacts if they exist."
        )
        hparams = parser.parse_args()

        output_dir = Path(hparams.output_dir).resolve()

        if not output_dir.exists():
            raise FileNotFoundError(f"The provided directory {output_dir} doesn't exist.")

        config = DownloadArtefactsConfig(include=hparams.include, exclude=hparams.exclude)
        response: List[str] = self.invoke_handler(config=config)

        if not response:
            return

        if len(response[0]) == 2:
            for path, url in response:
                if path.startswith("/"):
                    path = path[1:]
                resp = requests.get(url, allow_redirects=True)
                target_file = Path(os.path.join(output_dir, path))
                with open(target_file, "wb") as f:
                    f.write(resp.content)
        else:
            for path in response:
                source_path = Path(path).resolve()
                shared_storage = shared_storage_path()
                cleaned_path = (
                    str(path)
                    .replace(str(shared_storage) + "/", "")
                    .replace("/artifacts/", "")
                    .replace(os.getcwd() + "/", "")
                )

                target_file = Path(os.path.join(output_dir, cleaned_path))
                if not target_file.parent.exists():
                    os.makedirs(str(target_file.parent), exist_ok=True)
                copy_files(source_path, target_file)

        print("All the specified artifacts were downloaded.")


def _collect_artefact_urls(config: DownloadArtefactsConfig) -> List[Union[str, Tuple[str, str]]]:
    """This function is responsible to collect the files from the shared filesystem."""

    use_localhost = "LIGHTNING_APP_STATE_URL" not in os.environ

    if use_localhost:
        return _collect_artefact_paths(
            config=ShowArtefactsConfig(include=config.include, exclude=config.exclude),
            replace=False,
        )
    else:
        client = LightningClient()
        project_id = _get_project(client).project_id
        app_id = os.getenv("LIGHTNING_CLOUD_APP_ID")
        response = client.lightningapp_instance_service_list_lightningapp_instance_artifacts(project_id, app_id)
        paths = [artifact.filename for artifact in response.artifacts]
        maps = {artifact.filename: artifact.url for artifact in response.artifacts}
        filtered_paths = _filter_paths(paths, include=config.include, exclude=config.exclude)
        return [(path, maps[path]) for path in filtered_paths]
