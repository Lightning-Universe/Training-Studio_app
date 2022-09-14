import os
import subprocess
import sys
import uuid

from behave import then, when
from playwright.sync_api import expect, Page


@when("I execute lightning run notebook")
def step_impl(context):
    context.notebook_name = uuid.uuid4().hex

    cmd = [sys.executable, "-m", "lightning", "run", "notebook", f"--name={context.notebook_name}"]

    process = subprocess.Popen(
        cmd,
        env=os.environ.copy(),
    )
    process.wait()


@then("I can see a notebook in the UI")
def step_impl(context):
    page: Page = context.page

    locator = page.frame_locator("iframe").locator(f"text={context.notebook_name}")
    expect(locator).to_be_visible(timeout=60 * 1000)


@then("I can open the notebook")
def step_impl(context):
    page: Page = context.page

    locator = page.frame_locator("iframe").locator("table tbody tr", has_text=context.notebook_name)
    notebook_url = locator.locator("a", has_text="Open").get_attribute("href")
    page.goto(notebook_url)
    expect(page.locator("title")).to_have_text("JupyterLab")
