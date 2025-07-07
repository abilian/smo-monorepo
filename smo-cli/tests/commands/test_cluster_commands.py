from pathlib import Path

import pytest

from smo_cli.cli import main


@pytest.fixture
def mock_cluster_service(mocker):
    """Mocks the entire cluster_service module from smo_core."""
    return mocker.patch("smo_cli.commands.cluster.cluster_service")


def test_cluster_sync(runner, tmp_smo_dir: Path, mock_cluster_service):
    """Tests 'smo-cli cluster sync'."""

    # Configure the mock to return some data
    mock_cluster_service.fetch_clusters.return_value = [
        {
            "name": "cluster-1",
            "available_cpu": 8,
            "available_ram": "16Gi",
            "availability": True,
        },
        {
            "name": "cluster-2",
            "available_cpu": 4,
            "available_ram": "8Gi",
            "availability": False,
        },
    ]

    result = runner.invoke(main, ["cluster", "sync"])

    assert result.exit_code == 0
    assert "Successfully synced 2 cluster(s)" in result.output
    assert "cluster-1" in result.output
    assert "Not Ready" in result.output  # for cluster-2

    # Assert that the core service was called correctly
    mock_cluster_service.fetch_clusters.assert_called_once()


def test_cluster_list_no_db(runner, tmp_smo_dir: Path, mocker):
    """Tests 'smo-cli cluster list' when the DB doesn't exist yet."""

    # We patch the db_session to simulate an error, e.g., db not initialized
    mocker.patch(
        "smo_cli.core.context.CliContext.db_session",
        side_effect=Exception("DB file not found"),
    )

    result = runner.invoke(main, ["cluster", "list"])
    assert result.exit_code != 0
    assert "DB file not found" in result.output
