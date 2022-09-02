import argparse
import os
from typing import Dict, List, Optional

import rich
from lightning.app.utilities.commands import ClientCommand
from pydantic import BaseModel
from rich.text import Text
from rich.tree import Tree


def _walk_folder(tree: Tree, sorted_directories: Dict[str, List[str]], root_path: str, depth: int):
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
        _walk_folder(
            branch,
            {directory: sorted_directories[directory] for directory in directories},
            os.path.join(root_path, folder),
            depth + 1,
        )


def walk_folder(paths: List[str], tree: Tree) -> None:
    """Recursively build a Tree with directory contents."""
    paths = sorted(paths)
    directories = {}
    for p in paths:
        directory = os.path.dirname(p)
        if directory not in directories:
            directories[directory] = []
        directories[directory].append(p)

    _walk_folder(tree, directories, "artifacts", 1)
    rich.print(tree)


class ShowArtefactsConfig(BaseModel):
    filter_regex: Optional[str] = None


class ShowArtefactsCommand(ClientCommand):
    def run(self) -> None:
        # 1. Parse the user arguments.
        parser = argparse.ArgumentParser()
        parser.add_argument("--include", type=str, default=None, help="Provide a filtering regex.")
        parser.add_argument("--exclude", type=str, default=None, help="Provide a filtering regex.")
        hparams = parser.parse_args()

        config = ShowArtefactsConfig(filter_regex=hparams.filter)
        response: List[str] = self.invoke_handler(config=config)

        tree = Tree(
            "[bold magenta]:open_file_folder: root",
            guide_style="bold bright_blue",
        )

        walk_folder(response, tree)
