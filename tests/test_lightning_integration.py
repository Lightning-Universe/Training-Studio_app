from lightning.cli.lightning_cli import run_app
from click.testing import CliRunner

def test_lightning_import(caplog, monkeypatch):

    runner = CliRunner()
    result = runner.invoke(
        run_app,
        [
            "tests/integration_app/app.py",
            "--blocking",
            "False",
            "--open-ui",
            "False",
        ],
        catch_exceptions=False,
    )
    assert result.exit_code == 0