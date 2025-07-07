import os
from pathlib import Path
from textwrap import dedent

import pytest
import yaml
from click.testing import CliRunner

from smo_cli.cli import main


@pytest.fixture(scope="function")
def tmp_smo_dir(tmp_path: Path, runner: CliRunner) -> Path:
    """
    Creates a temporary directory for ~/.smo, which is used by the tests.
    This ensures that tests do not interfere with the user's actual SMO configuration.
    """
    smo_dir = tmp_path / ".smo"
    os.environ["SMO_DIR"] = str(smo_dir)
    assert runner.invoke(main, ["init"]).exit_code == 0
    return smo_dir


@pytest.fixture(scope="function")
def mock_smo_env(tmp_path: Path, monkeypatch) -> Path:
    """
    Creates a temporary directory for ~/.smo, points the config to it,
    and creates a default config file. This isolates tests from the user's
    actual SMO configuration.
    """
    # smo_path = tmp_path / ".smo"
    # smo_path.mkdir()
    #
    # # Use monkeypatch to redirect the config/db constants to our temp directory
    # monkeypatch.setattr(
    #     "smo_cli.core.config.SMO_DIR",
    #     str(smo_path),
    # )
    # monkeypatch.setattr(
    #     "smo_cli.core.config.CONFIG_FILE", str(smo_path / "config.yaml")
    # )
    # monkeypatch.setattr(
    #     "smo_cli.core.database.DB_FILE",
    #     str(smo_path / "smo.db"),
    # )
    #
    # # Create a dummy config file
    # config_path = str(smo_path / "config.yaml")
    # config_data = {
    #     "karmada_kubeconfig": "/tmp/fake-karmada.config",
    #     "grafana": {
    #         "host": "http://mock-grafana",
    #         "username": "admin",
    #         "password": "password",
    #     },
    #     "prometheus_host": "http://mock-prometheus",
    #     "helm": {"insecure_registry": True},
    #     "scaling": {"interval_seconds": 30},
    # }
    # with open(config_path, "w") as f:
    #     yaml.dump(config_data, f)
    #
    # return smo_path


@pytest.fixture
def runner():
    """Provides a Click CliRunner instance for invoking commands."""
    return CliRunner()


@pytest.fixture
def mock_graph_service(mocker):
    """Mocks the entire graph_service module from smo_core."""
    return mocker.patch("smo_cli.commands.graph.graph_service")


@pytest.fixture
def hdag_file(tmp_path: Path):
    """Creates a temporary HDAG descriptor file for testing."""
    hdag_content = dedent(
        """
        hdaGraph:
          id: my-test-graph
          services:
            - id: service-a
            - id: service-b
        """
    )
    f = tmp_path / "hdag.yaml"
    f.write_text(hdag_content)
    return str(f)
