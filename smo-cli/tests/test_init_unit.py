import os
from pathlib import Path

from smo_cli.commands.init import _init


def test_init(tmp_path: Path) -> None:
    """
    Tests the function undelying the 'smo-cli init' command.
    """
    smo_dir = tmp_path / ".smo"
    os.environ["SMO_DIR"] = str(smo_dir)

    _init()
    assert (smo_dir / "config.yaml").exists()
    assert (smo_dir / "smo.db").exists()
