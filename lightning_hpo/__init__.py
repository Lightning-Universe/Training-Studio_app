"""Root package info."""
import logging
import os

_root_logger = logging.getLogger()
_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

_console = logging.StreamHandler()
_console.setLevel(logging.INFO)

formatter = logging.Formatter("%(levelname)s: %(message)s")
_console.setFormatter(formatter)

# if root logger has handlers, propagate messages up and let root logger process them,
# otherwise use our own handler
if not _root_logger.hasHandlers():
    _logger.addHandler(_console)
    _logger.propagate = False


from lightning_hpo.__about__ import *  # noqa: E402, F401, F403
import lightning_hpo as L_Hpo  # noqa: E402

_PACKAGE_ROOT = os.path.dirname(__file__)
_PROJECT_ROOT = os.path.dirname(_PACKAGE_ROOT)

__all__ = ["L_Hpo.optuna.objective.BaseObjectiveWork", "L_Hpo.optuna_flow.OptunaPythonScript"]


def exported_lightning_components():
    return [L_Hpo.optuna_flow.OptunaPythonScript, L_Hpo.optuna.objective.BaseObjectiveWork]
