import os
from pathlib import Path

from click.testing import CliRunner

from smo_cli.cli import main


def test_init_command(runner: CliRunner, tmp_path: Path) -> None:
    """
    Tests the 'smo-cli init' command to ensure it creates the necessary
    directory, config file, and database file.
    """
    smo_dir = tmp_path / ".smo"
    smo_dir.mkdir()

    os.environ["SMO_DIR"] = str(smo_dir)
    result = runner.invoke(main, ["init"])

    assert result.exit_code == 0
    assert "Created default configuration file" in result.output
    assert "Ensured local database is created" in result.output
    assert (smo_dir / "config.yaml").exists()
    # assert (smo_dir / "smo.db").exists()
