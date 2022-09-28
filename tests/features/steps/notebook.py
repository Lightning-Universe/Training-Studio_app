import os
import subprocess
import sys
import uuid

from behave import given, then, when
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


@when("I execute lightning stop notebook")
def step_impl(context):
    cmd = [sys.executable, "-m", "lightning", "stop", "notebook", f"--name={context.notebook_name}"]

    process = subprocess.Popen(
        cmd,
        env=os.environ.copy(),
    )
    process.wait()


@when("I execute lightning show notebooks")
def step_impl(context):
    cmd = [sys.executable, "-m", "lightning", "show", "notebooks"]

    process = subprocess.Popen(
        cmd,
        env=os.environ.copy(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    process.wait()

    context.stdout = process.stdout.read().decode("UTF-8")
    context.stderr = process.stderr.read().decode("UTF-8")


@given("a notebook is running")
def step_impl(context):
    context.execute_steps(
        """
        When I execute lightning run notebook
    """
    )

    page: Page = context.page

    locator = page.frame_locator("iframe").locator("table tbody tr", has_text=context.notebook_name)
    locator = locator.locator("text=Running")
    locator.wait_for(timeout=60 * 1000)


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


def check_notebook_status_ui(context, status):
    page: Page = context.page

    locator = page.frame_locator("iframe").locator("table tbody tr", has_text=context.notebook_name)
    locator = locator.locator(f"text={status}")
    expect(locator).to_be_visible(timeout=60 * 1000)


@then("the notebook status in the UI is stopped")
def step_impl(context):
    check_notebook_status_ui(context, "Stopped")


@then("the notebook status in the UI is running")
def step_impl(context):
    check_notebook_status_ui(context, "Running")


@then("I can see a notebook in the terminal")
def step_impl(context):
    # Notebook name can be clipped so just look for first 8 characters
    assert context.notebook_name[:8] in context.stdout


def check_notebook_status_terminal(context, status):
    header_row = next(filter(lambda line: "name" in line, context.stdout.split("\n")))
    keys = [key.strip() for key in header_row.split("┃")[1:-1]]

    notebook_row = next(filter(lambda line: context.notebook_name[:8] in line, context.stdout.split("\n")))
    values = [value.strip() for value in notebook_row.split("│")[1:-1]]

    notebook_details = {key: value for key, value in zip(keys, values)}
    assert notebook_details["status"] == status


@then("the notebook status in the terminal is stopped")
def step_impl(context):
    check_notebook_status_terminal(context, "stopped")


@then("the notebook status in the terminal is running")
def step_impl(context):
    check_notebook_status_terminal(context, "running")
