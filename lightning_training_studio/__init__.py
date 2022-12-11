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

from lightning_training_studio.__about__ import *  # noqa: E402, F401, F403
from lightning_training_studio.components.sweep import Sweep  # noqa: E402
from lightning_training_studio.framework.agnostic import Objective  # noqa: E402
from lightning_training_studio.utilities.utils import HPOCloudCompute  # noqa: E402, F401

_PACKAGE_ROOT = os.path.dirname(__file__)
_PROJECT_ROOT = os.path.dirname(_PACKAGE_ROOT)

from optuna.storages._in_memory import _logger

_logger.disabled = True
_logger.propagate = False

__all__ = ["Objective", "Sweep", "HPOCloudCompute"]
