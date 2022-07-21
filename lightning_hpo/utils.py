import shutil
from typing import Optional
from lightning.app.storage import Path
from lightning import LightningFlow
import os
import tarfile

def get_best_model_path(flow: LightningFlow) -> Optional[Path]:
    metrics = {work.best_model_score: work for work in flow.works()}
    if not all(metrics):
        return None

    if all(metric is None for metric in metrics):
        return None

    return metrics[max(metrics)].best_model_path

def clean_tarfile(file_path: str, mode):
    if os.path.exists(file_path):
        with tarfile.open(file_path, mode=mode) as tar_ref:
            for member in tar_ref.getmembers():
                p = member.path
                if p != '.' and os.path.exists(p):
                    if os.path.isfile(p):
                        os.remove(p)
                    else:
                        shutil.rmtree(p)
        os.remove(file_path)


def extract_tarfile(file_path: str, extract_path: str, mode: str):
    if os.path.exists(file_path):
        with tarfile.open(file_path, mode=mode) as tar_ref:
            for member in tar_ref.getmembers():
                try:
                    tar_ref.extract(member, path=extract_path, set_attrs=False)
                except PermissionError:
                    raise PermissionError(f"Could not extract tar file {file_path}")