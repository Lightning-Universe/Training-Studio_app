import os
import subprocess
import sys
import tempfile
import time

import psutil
from behave import fixture, use_fixture
from lightning.app.cli.lightning_cli import get_app_url
from lightning.app.runners.runtime_type import RuntimeType
from playwright.sync_api import expect, sync_playwright

from lightning_training_studio import _PROJECT_ROOT


def kill(proc_pid):
    process = psutil.Process(proc_pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()


@fixture
def run_app(context):
    cmd = [
        sys.executable,
        "-m",
        "lightning",
        "run",
        "app",
        os.path.join(_PROJECT_ROOT, "app.py"),
        "--open-ui",
        "False",
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        os.chmod(tmpdir, 0o777)
        # TODO: Doesn't work if you pass tmpdir as cwd to the Popen call
        os.chdir(tmpdir)
        process = subprocess.Popen(cmd, env=os.environ.copy(), preexec_fn=os.setsid)

        context.app_id = "localhost"

        with sync_playwright() as p:
            context.browser = p.chromium.launch()
            context.page = context.browser.new_page()

            while True:
                try:
                    time.sleep(5)
                    context.page.goto(get_app_url(RuntimeType.MULTIPROCESS))
                    locator = context.page.frame_locator("iframe").locator("text=Training Studio")
                    expect(locator).to_be_visible(timeout=30 * 1000)
                    break
                except:  # noqa: E722
                    pass

            yield context.browser

            context.browser.close()

        print("Killing App Process")
        kill(process.pid)


def before_scenario(context, scenario):
    use_fixture(run_app, context)
