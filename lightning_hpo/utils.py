from typing import Optional
from lightning.app.storage import Path
from lightning import LightningFlow

def get_best_model_path(flow: LightningFlow) -> Optional[Path]:
    metrics = {work.best_model_score: work for work in flow.works()}
    if not all(metrics):
        return None

    if all(metric is None for metric in metrics):
        return None

    return metrics[max(metrics)].best_model_path