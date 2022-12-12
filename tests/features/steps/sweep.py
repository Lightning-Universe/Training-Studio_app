import os
import subprocess
import sys
import uuid

from behave import given, then, when
from playwright.sync_api import expect, Page

from lightning_training_studio import _PROJECT_ROOT


@when("I execute lightning run sweep")
def step_impl(context):
    context.sweep_name = uuid.uuid4().hex

    cmd = [
        sys.executable,
        "-m",
        "lightning",
        "run",
        "sweep",
        os.path.abspath(os.path.join(_PROJECT_ROOT, "examples", "scripts", "train.py")),
        f"--name={context.sweep_name}",
        "--total_experiments=5",
        "--logger=tensorboard",
        "--direction=maximize",
        "--model.lr='log_uniform(0.001, 0.01)'",
        "--model.gamma='uniform(0.5, 0.8)'",
        "--data.batch_size='categorical([32, 64])'",
    ]

    process = subprocess.Popen(
        cmd,
        env=os.environ.copy(),
    )
    process.wait()


@when("I execute lightning stop sweep")
def step_impl(context):
    cmd = [sys.executable, "-m", "lightning", "stop", "sweep", f"--name={context.sweep_name}"]

    process = subprocess.Popen(
        cmd,
        env=os.environ.copy(),
    )
    process.wait()


@when("I execute lightning show sweeps")
def step_impl(context):
    cmd = [sys.executable, "-m", "lightning", "show", "sweeps"]

    process = subprocess.Popen(
        cmd,
        env=os.environ.copy(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    process.wait()

    context.stdout = process.stdout.read().decode("UTF-8")
    context.stderr = process.stderr.read().decode("UTF-8")


@then("I can see a sweep in the UI")
def step_impl(context):
    page: Page = context.page
    page.frame_locator("iframe").locator("text=Sweeps & Experiments").click()

    locator = page.frame_locator("iframe").locator(f"text={context.sweep_name}")
    expect(locator).to_be_visible(timeout=60 * 1000)


@then("I can open the logger")
def step_impl(context):
    page: Page = context.page

    locator = page.frame_locator("iframe").locator("table tbody tr", has_text=context.sweep_name)
    logger_url = locator.locator("a", has_text="Open").get_attribute("href")
    page.goto(logger_url)
    expect(page).to_have_title("TensorBoard")


def check_sweep_status_ui(context, status):
    page: Page = context.page
    page.frame_locator("iframe").locator("text=Sweeps & Experiments").click()

    locator = page.frame_locator("iframe").locator("table tbody tr", has_text=context.sweep_name)
    locator = locator.locator(f"text={status}")
    expect(locator).to_be_visible(timeout=60 * 1000)


@then("the sweep status in the UI is stopped")
def step_impl(context):
    check_sweep_status_ui(context, "Stopped")


@then("the sweep status in the UI is running")
def step_impl(context):
    check_sweep_status_ui(context, "Running")


@then("I can see a sweep in the terminal")
def step_impl(context):
    # Sweep name can be clipped so just look for first 8 characters
    assert context.sweep_name[:8] in context.stdout


def check_sweep_status_terminal(context, status):
    header_row = next(filter(lambda line: "name" in line, context.stdout.split("\n")))
    keys = [key.strip() for key in header_row.split("┃")[1:-1]]

    sweep_row = next(filter(lambda line: context.sweep_name[:8] in line, context.stdout.split("\n")))
    values = [value.strip() for value in sweep_row.split("│")[1:-1]]

    sweep_details = {key: value for key, value in zip(keys, values)}
    assert sweep_details["status"] == status


@then("the sweep status in the terminal is stopped")
def step_impl(context):
    check_sweep_status_terminal(context, "stopped")


@then("the sweep status in the terminal is running")
def step_impl(context):
    check_sweep_status_terminal(context, "running")


@given("a sweep is running")
def step_impl(context):
    context.execute_steps(
        """
        When I execute lightning run sweep
        Then the sweep status in the UI is running
    """
    )
