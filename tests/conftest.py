import os
import shutil
import threading
from threading import Thread

import psutil
import pytest
from lightning.app.storage.path import _storage_root_dir
from lightning.app.utilities.component import _set_context
from lightning.app.utilities.packaging.app_config import _APP_CONFIG_FILENAME

original_method = Thread._wait_for_tstate_lock


def fn(self, *args, timeout=None, **kwargs):
    original_method(self, *args, timeout=1, **kwargs)


Thread._wait_for_tstate_lock = fn


def pytest_sessionfinish(session, exitstatus):
    """Pytest hook that get called after whole test run finished, right before returning the exit status to the
    system."""
    # kill all the processes and threads created by parent
    # TODO This isn't great. We should have each tests doing it's own cleanup
    current_process = psutil.Process()
    for child in current_process.children(recursive=True):
        try:
            params = child.as_dict() or {}
            cmd_lines = params.get("cmdline", [])
            # we shouldn't kill the resource tracker from multiprocessing. If we do,
            # `atexit` will throw as it uses resource tracker to try to clean up
            if cmd_lines and "resource_tracker" in cmd_lines[-1]:
                continue
            child.kill()
        except Exception:
            pass

    main_thread = threading.current_thread()
    for t in threading.enumerate():
        if t is not main_thread:
            t.join(0)


@pytest.fixture(scope="function", autouse=True)
def cleanup():
    from lightning.app.utilities.app_helpers import _LightningAppRef

    yield
    _LightningAppRef._app_instance = None
    shutil.rmtree("./storage", ignore_errors=True)
    shutil.rmtree(_storage_root_dir(), ignore_errors=True)
    shutil.rmtree("./.shared", ignore_errors=True)
    if os.path.isfile(_APP_CONFIG_FILENAME):
        os.remove(_APP_CONFIG_FILENAME)
    _set_context(None)
