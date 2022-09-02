import argparse
import os
import re
from typing import Dict, List, Optional

import rich
from lightning.app.storage.path import filesystem, shared_storage_path
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
    include: Optional[str] = None
    exclude: Optional[str] = None


class ShowArtefactsCommand(ClientCommand):
    def run(self) -> None:
        # 1. Parse the user arguments.
        parser = argparse.ArgumentParser()
        parser.add_argument("--include", type=str, default=None, help="Provide a regex to include some specific files.")
        parser.add_argument("--exclude", type=str, default=None, help="Provide a regex to exclude some specific files.")
        hparams = parser.parse_args()

        config = ShowArtefactsConfig(include=hparams.include, exclude=hparams.exclude)
        response: List[str] = self.invoke_handler(config=config)

        tree = Tree(
            "[bold magenta]:open_file_folder: root",
            guide_style="bold bright_blue",
        )

        walk_folder(response, tree)


def _filter_paths(paths: List[str], include: Optional[str], exclude: Optional[str]) -> List[str]:
    out = []

    if include:
        include_pattern = re.compile(include)

    if exclude:
        exclude_pattern = re.compile(exclude)

    for path in paths:
        if include or exclude:
            if exclude and len(exclude_pattern.findall(path)):
                pass

            elif (include and len(include_pattern.findall(path))) or include is None:
                out.append(path)
        else:
            out.append(path)
    return out


def _collect_artefact_paths(config: ShowArtefactsConfig, replace: bool = True) -> List[str]:
    """This function is responsible to collecting the files from the shared filesystem."""
    fs = filesystem()
    paths = []

    shared_storage = shared_storage_path()
    for root_dir, _, files in fs.walk(shared_storage):
        if replace:
            root_dir = str(root_dir).replace(str(shared_storage), "").replace("/artifacts/root.", "root/")
        for f in files:
            paths.append(os.path.join(str(root_dir), f))

    return _filter_paths(paths, config.include, config.exclude)
