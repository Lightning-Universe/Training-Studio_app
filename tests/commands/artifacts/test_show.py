import os
import os.path as osp
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import requests

from lightning_training_studio.commands.artifacts import show
from lightning_training_studio.commands.artifacts.show import ShowArtifactsCommand, ShowArtifactsConfigResponse


def test_show_artifacts(monkeypatch, tmpdir):

    original_sys_argv = sys.argv

    with tempfile.TemporaryDirectory() as tmp:

        # 1: Create some shared files.
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
        resp.json.return_value = ShowArtifactsConfigResponse(sweep_names=[], experiment_names=["b"], paths=paths).dict()
        resp.status_code = 200
        post = MagicMock(return_value=resp)
        monkeypatch.setattr(requests, "post", post)

        monkeypatch.setattr(show, "_shared_storage_path", lambda: tmp)
        print_mock = MagicMock()
        monkeypatch.setattr(show.rich, "print", print_mock)

        output_dir = osp.join(str(tmpdir), ".shared/")
        os.makedirs(output_dir)
        sys.argv = ["", "--display_mode", "tree", "--names", "b"]
        command = ShowArtifactsCommand(None)
        command.command_name = ""
        command.app_url = ""
        command.run()

        tree = print_mock._mock_call_args.args[0]
        assert isinstance(tree, show.Tree)

        counter = 0
        has_checked = False
        while tree.children:
            tree = tree.children[0]
            counter += 1
            if len(tree.children) == 2:
                assert tree.children[0].label == "[bold magenta]:open_file_folder: a"
                assert tree.children[1].label == "[bold magenta]:open_file_folder: d"
                has_checked = True
        assert has_checked
        assert "📄 " in tree.label._text[0]

    sys.argv = original_sys_argv
