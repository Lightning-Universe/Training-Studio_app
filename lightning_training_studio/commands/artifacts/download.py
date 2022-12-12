import argparse
import math
import os
from pathlib import Path
from typing import List, Optional, Tuple

import requests
from lightning.app.utilities.cloud import _get_project
from lightning.app.utilities.commands import ClientCommand
from lightning.app.utilities.network import LightningClient
from pydantic import BaseModel
from tqdm.auto import tqdm

from lightning_training_studio.commands.artifacts.show import (
    _collect_artifact_paths,
    _filter_paths,
    ShowArtifactsConfig,
)


def _download_file(url: str, target_file: str):
    target_file = Path(target_file).resolve()
    target_file.parent.mkdir(exist_ok=True, parents=True)

    response = requests.get(url, allow_redirects=True, stream=True)
    total_length = response.headers.get("content-length", None)

    with open(target_file, "wb") as target:
        if total_length is None:
            target.write(response.content)
        else:
            total_length = int(total_length)
            chunk_size = 1024  # 1 KB
            for chunk in tqdm(
                response.iter_content(chunk_size=chunk_size),
                total=int(total_length / chunk_size),
                unit="KB",
                desc=str(target_file.name),
                leave=True,  # progressbar stays
            ):
                target.write(chunk)


def _copy_file(source_file: str, target_file: str):
    source_file = Path(source_file).resolve()
    target_file = Path(target_file).resolve()
    target_file.parent.mkdir(exist_ok=True, parents=True)

    total_length = os.stat(source_file).st_size

    with open(target_file, "wb") as target:
        with open(source_file, "rb") as source:
            chunk_size = 1024  # 1 KB
            chunks = math.ceil(total_length / chunk_size)
            for i in tqdm(
                range(chunks),
                total=chunks,
                unit="KB",
                desc=str(target_file.name),
                leave=True,  # progressbar stays
            ):
                target.write(source.read(chunk_size))


class DownloadArtifactsConfig(BaseModel):
    include: Optional[str] = None
    exclude: Optional[str] = None


class DownloadArtifactsConfigResponse(BaseModel):
    sweep_names: List[str]
    experiment_names: List[str]
    paths: List[str]
    urls: Optional[List[str]]


class DownloadArtifactsCommand(ClientCommand):

    description = "Download artifacts for experiments or sweeps."

    def run(self) -> None:
        # 1. Parse the user arguments.
        parser = argparse.ArgumentParser()
        parser.add_argument("--names", nargs="+", default=[], help="Provide a list of experiments or sweep names.")
        parser.add_argument(
            "--output_dir", required=True, type=str, help="Provide the output directory for the artifacts.."
        )
        hparams = parser.parse_args()

        output_dir = Path(hparams.output_dir).resolve()

        if not output_dir.exists():
            output_dir.mkdir(exist_ok=True)

        config = DownloadArtifactsConfig(include=None, exclude=None)
        response = DownloadArtifactsConfigResponse(**self.invoke_handler(config=config))

        for name in hparams.names:
            has_found = False
            if name in response.sweep_names:
                has_found = True
            elif name in response.experiment_names:
                has_found = True

            if not has_found:
                raise ValueError(
                    f"The provided name `{name}` doesn't exists. "
                    f" Here are the available Sweeps {response.sweep_names} and "
                    f"available Experiments {response.experiment_names}."
                )

        if response.urls:
            for path, url in zip(response.paths, response.urls):
                if not any(name in path for name in hparams.names):
                    continue
                if path.startswith("/"):
                    path = path[1:]
                if path.startswith("drive/"):
                    path = path.split("drive/")[1]
                _download_file(url, os.path.join(output_dir, path))
        else:
            for path in response.paths:
                if not any(name in path for name in hparams.names):
                    continue
                path = str(path)
                if "drive/" in path:
                    output_path = os.path.join(output_dir, path.split("drive/")[1])
                _copy_file(path, output_path)

        print("All the specified artifacts were downloaded.")


def _collect_artifact_urls(config: DownloadArtifactsConfig) -> Tuple[List[str], Optional[List[str]]]:
    """This function is responsible to collect the files from the shared filesystem."""

    use_localhost = "LIGHTNING_APP_STATE_URL" not in os.environ

    if use_localhost:
        paths = _collect_artifact_paths(
            config=ShowArtifactsConfig(include=config.include, exclude=config.exclude),
            replace=False,
        )
        return paths, None
    else:
        client = LightningClient()
        project_id = _get_project(client).project_id
        app_id = os.getenv("LIGHTNING_CLOUD_APP_ID")
        response = client.lightningapp_instance_service_list_lightningapp_instance_artifacts(project_id, app_id)
        paths = [artifact.filename for artifact in response.artifacts]
        maps = {artifact.filename: artifact.url for artifact in response.artifacts}
        filtered_paths = _filter_paths(paths, include=config.include, exclude=config.exclude)
        return filtered_paths, [maps[path] for path in filtered_paths]
