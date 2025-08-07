import os
from pathlib import Path

from sqlalchemy import create_engine

from smo_cli.commands.init import do_init
from smo_cli.console import Console


def test_init(tmp_path: Path) -> None:
    """
    Tests the function undelying the 'smo-cli init' command.
    """
    smo_dir = tmp_path / ".smo"
    os.environ["SMO_DIR"] = str(smo_dir)

    engine = create_engine("sqlite:///" + str(smo_dir / "smo.db"))
    console = Console()
    do_init(engine, console)

    assert (smo_dir / "config.yaml").exists()
    assert (smo_dir / "smo.db").exists()
