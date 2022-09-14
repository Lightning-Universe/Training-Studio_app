import os
import subprocess
import sys
import tempfile
import time

import playwright
from behave import fixture, use_fixture
from lightning_app.cli.lightning_cli import get_app_url
from lightning_app.runners.runtime_type import RuntimeType
from playwright.sync_api import expect, sync_playwright

from lightning_hpo import _PROJECT_ROOT


@fixture
def run_app(context):
    cmd = [
        sys.executable,
        "-m",
        "lightning",
        "run",
        "app",
        os.path.join(_PROJECT_ROOT, "training_studio_app.py"),
        "--open-ui",
        "False",
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        os.chmod(tmpdir, 0o777)
        # TODO: Doesn't work if you pass tmpdir as cwd to the Popen call
        os.chdir(tmpdir)
        process = subprocess.Popen(
            cmd,
            env=os.environ.copy(),
        )

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
                except (
                    playwright._impl._api_types.Error,
                    playwright._impl._api_types.TimeoutError,
                ):
                    pass

            yield context.browser

            context.browser.close()
        process.terminate()
        process.wait()


def before_scenario(context, scenario):
    use_fixture(run_app, context)
