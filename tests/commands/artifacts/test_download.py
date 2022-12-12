import os
import os.path as osp
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import requests

from lightning_training_studio.commands.artifacts.download import (
    DownloadArtifactsCommand,
    DownloadArtifactsConfigResponse,
)


def test_download_artifacts(monkeypatch, tmpdir):

    original_sys_argv = sys.argv

    with tempfile.TemporaryDirectory() as tmp:

        path = Path(osp.join(tmp, "a/something/drive/c/example.txt"))
        os.makedirs(path.parent, exist_ok=True)
        with open(path, "w") as f:
            f.write("example.txt")

        path = Path(osp.join(tmp, "e/d/drive/f/example.txt"))
        os.makedirs(path.parent, exist_ok=True)
        with open(path, "w") as f:
            f.write("example.txt")

        paths = []
        for d, _, files in os.walk(tmp):
            for f in files:
                paths.append(osp.join(d, f))

        resp = MagicMock()
        resp.json.return_value = DownloadArtifactsConfigResponse(
            paths=paths, sweep_names=[], experiment_names=["something"], urls=None
        ).dict()
        resp.status_code = 200
        post = MagicMock(return_value=resp)
        monkeypatch.setattr(requests, "post", post)

        output_dir = osp.join(str(tmpdir), "new_folder")
        os.makedirs(output_dir)
        sys.argv = ["", "--output_dir", output_dir, "--names", "something"]
        command = DownloadArtifactsCommand(None)
        command.command_name = ""
        command.app_url = ""
        command.run()
        assert osp.exists(osp.join(output_dir, "c/example.txt"))
        assert not osp.exists(osp.join(output_dir, "f/example.txt"))

    sys.argv = original_sys_argv
