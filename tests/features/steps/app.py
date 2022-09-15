import os
import subprocess
import sys

from behave import given


@given("I am connected to the app")
def step_impl(context):
    cmd = [
        sys.executable,
        "-m",
        "lightning",
        "connect",
        context.app_id,
    ]

    process = subprocess.Popen(
        cmd,
        env=os.environ.copy(),
    )
    process.wait()
