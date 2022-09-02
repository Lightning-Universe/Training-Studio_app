import os
import os.path as osp
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import requests

from lightning_hpo.commands.artefacts import download
from lightning_hpo.commands.artefacts.download import DownloadArtefactsCommand


def test_download_artefacts(monkeypatch, tmpdir):

    original_sys_argv = sys.argv

    with tempfile.TemporaryDirectory() as tmp:

        path = Path(osp.join(tmp, "a/b/c/d/example.txt"))
        os.makedirs(path.parent, exist_ok=True)
        with open(path, "w") as f:
            f.write("example.txt")

        path = Path(osp.join(tmp, "d/a/b/c/example.txt"))
        os.makedirs(path.parent, exist_ok=True)
        with open(path, "w") as f:
            f.write("example.txt")

        paths = []
        for d, _, files in os.walk(tmp):
            for f in files:
                paths.append(osp.join(d, f))

        resp = MagicMock()
        resp.json.return_value = paths
        resp.status_code = 200
        post = MagicMock(return_value=resp)
        monkeypatch.setattr(requests, "post", post)

        monkeypatch.setattr(download, "shared_storage_path", lambda: tmp)

        output_dir = osp.join(str(tmpdir), ".shared/")
        os.makedirs(output_dir)
        sys.argv = ["", output_dir, "--include=a/b"]
        command = DownloadArtefactsCommand(None)
        command.command_name = ""
        command.app_url = ""
        command.run()

        assert osp.exists(osp.join(output_dir, "a/b/c/d/example.txt"))
        assert osp.exists(osp.join(output_dir, "d/a/b/c/example.txt"))

    sys.argv = original_sys_argv
