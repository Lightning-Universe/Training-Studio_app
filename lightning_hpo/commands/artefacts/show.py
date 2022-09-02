import argparse
import os
from typing import Any, Dict, List, Optional

import requests
import rich
from lightning.app.utilities.commands import ClientCommand
from pydantic import BaseModel
from rich.text import Text
from rich.tree import Tree


def walk_folder(tree, sorted_directories, root_path, depth):
    parents = {}
    for directory in sorted_directories:
        splits = directory.split("/")
        if depth == len(splits):
            for path in sorted_directories[directory]:
                text_filename = Text(path.replace(directory + "/", ""), "green")
                text_filename.highlight_regex(r"\..*$", "bold red")
                text_filename.stylize(f"link {path}")
                icon = "🐍 " if path.endswith(".py") else "📄 "
                tree.add(Text(icon) + text_filename)
        else:
            root_folder = "/".join(splits[1 : depth + 1])  # noqa E203
            if root_folder not in parents:
                parents[root_folder] = []
            parents[root_folder].append(directory)

    if not parents:
        return

    for root_folder, directories in parents.items():
        folder = root_folder.split("/")[-1]
        style = "dim" if root_folder.startswith("__") else ""
        branch = tree.add(
            f"[bold magenta]:open_file_folder: {folder}",
            style=style,
            guide_style=style,
        )
        walk_folder(
            branch,
            {directory: sorted_directories[directory] for directory in directories},
            os.path.join(root_path, folder),
            depth + 1,
        )


def walk_directory(paths: List[str], tree: Tree) -> None:
    """Recursively build a Tree with directory contents."""
    paths = sorted(paths)
    directories = {}
    for p in paths:
        directory = os.path.dirname(p)
        if directory not in directories:
            directories[directory] = []
        directories[directory].append(p)

    walk_folder(tree, directories, "artifacts", 1)
    rich.print(tree)


class ShowArtefactsCommand(ClientCommand):

    # TODO: (tchaton) Upstream to Lightning
    def invoke_handler(self, config: Optional[BaseModel] = None) -> Dict[str, Any]:
        command = self.command_name.replace(" ", "_")
        resp = requests.post(self.app_url + f"/command/{command}", data=config.json() if config else None)
        assert resp.status_code == 200, resp.json()
        return resp.json()

    def run(self) -> None:
        # 1. Parse the user arguments.
        parser = argparse.ArgumentParser()
        parser.add_argument("--filter", type=str, default=None, help="Provide a filtering regex.")
        _ = parser.parse_args()

        response: List[str] = self.invoke_handler()

        tree = Tree(
            "[bold magenta]:open_file_folder: root",
            guide_style="bold bright_blue",
        )

        walk_directory(response, tree)
