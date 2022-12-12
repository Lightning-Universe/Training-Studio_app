import argparse
import os
import re
from typing import Dict, List, Optional

import rich
from lightning.app.storage.path import _filesystem, _shared_storage_path
from lightning.app.utilities.commands import ClientCommand
from pydantic import BaseModel
from rich.color import ANSI_COLOR_NAMES
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


def walk_folder_tree(paths: List[str], tree: Tree) -> None:
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


def walk_folder_flat_(paths: List[str]) -> None:
    colors = list(ANSI_COLOR_NAMES)
    paths = sorted(paths)
    mapping = {}
    counter = 1
    showed = {}
    for path in paths:
        splits = path.split("/")

        for idx in range(1, len(splits)):
            directory = "/".join(splits[:idx])
            if directory not in showed:
                showed[directory] = True
                rich.print(directory)

        for split in splits:
            if split not in mapping:
                mapping[split] = colors[counter]
                counter += 1

        colored_splits = []
        for split_idx, split in enumerate(splits, 1):
            color = mapping[split] if split_idx == len(splits) else colors[0]
            colored_split = f"[{color}]{split}[/{color}]"
            colored_splits.append(colored_split)
        colored_path = "/".join(colored_splits)
        rich.print(colored_path)


def _walk_folder_flat(tree: List[str], sorted_directories: Dict[str, List[str]], root_path: str, depth: int):
    parents = {}
    for directory in sorted_directories:
        splits = directory.split("/")
        if depth == len(splits):
            for path in sorted_directories[directory]:
                tree.append(path)
        else:
            root_folder = "/".join(splits[1 : depth + 1])  # noqa E203
            if root_folder not in parents:
                parents[root_folder] = []
            parents[root_folder].append(directory)

    if not parents:
        return

    for root_folder, directories in parents.items():
        folder = root_folder.split("/")[-1]
        root_folder = f":open_file_folder: /{root_folder}/"
        tree.append(f"[black]{root_folder}[/black]")
        _walk_folder_flat(
            tree,
            {directory: sorted_directories[directory] for directory in directories},
            os.path.join(root_path, folder),
            depth + 1,
        )


def _add_colors(filename: str) -> str:
    colors = list(ANSI_COLOR_NAMES)
    color = "magenta"

    if ".yaml" in filename:
        color = colors[1]

    elif ".ckpt" in filename:
        color = colors[2]

    elif "events.out.tfevents" in filename:
        color = colors[3]

    elif ".py" in filename:
        color = colors[4]

    elif ".png" in filename:
        color = colors[5]

    return f"[{color}]{filename}[/{color}]"


def walk_folder_flat(paths: List[str]) -> None:
    """Recursively build a Tree with directory contents."""
    paths = sorted(paths)
    directories = {}
    tree = []
    for p in paths:
        directory = os.path.dirname(p)
        if directory not in directories:
            directories[directory] = []
        directories[directory].append(p)

    _walk_folder_flat(tree, directories, "artifacts", 1)

    for path in tree:
        if not path.startswith("[black"):
            splits = path.split("/")
            path = f'   [black]{"/".join(splits[:-1])}[/black]/{_add_colors(splits[-1])}'
        rich.print(path)


class ShowArtifactsConfig(BaseModel):
    include: Optional[str] = None
    exclude: Optional[str] = None


class ShowArtifactsConfigResponse(BaseModel):
    sweep_names: List[str]
    experiment_names: List[str]
    paths: List[str]


class ShowArtifactsCommand(ClientCommand):

    description = "Show artifacts for experiments or sweeps, in flat or tree layout."

    def run(self) -> None:
        # 1. Parse the user arguments.
        parser = argparse.ArgumentParser()
        parser.add_argument("--names", nargs="+", default=[], help="Provide a list of experiments or sweep names.")
        parser.add_argument(
            "--display_mode",
            default="flat",
            choices=["flat", "tree"],
            help="Structure of the files displayed in the terminal",
        )
        hparams = parser.parse_args()

        config = ShowArtifactsConfig(include=None, exclude=None)
        response = ShowArtifactsConfigResponse(**self.invoke_handler(config=config))

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

        include = None
        if hparams.names:
            include = "|".join(hparams.names)

        paths = _filter_paths(response.paths, include=include, exclude=None)

        if hparams.display_mode == "tree":
            tree = Tree(
                "[bold magenta]:open_file_folder: root",
                guide_style="bold bright_blue",
            )

            walk_folder_tree(paths, tree)
        else:
            walk_folder_flat(paths)


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


def _collect_artifact_paths(config: ShowArtifactsConfig, replace: bool = True) -> List[str]:
    """This function is responsible to collecting the files from the shared filesystem."""
    fs = _filesystem()
    paths = []

    shared_storage = _shared_storage_path()
    for root_dir, _, files in fs.walk(shared_storage):
        if replace:
            root_dir = str(root_dir).replace(str(shared_storage), "").replace("/artifacts/drive", "")
        for f in files:
            paths.append(os.path.join(str(root_dir), f))

    return _filter_paths(paths, config.include, config.exclude)
