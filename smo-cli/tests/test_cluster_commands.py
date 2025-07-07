from pathlib import Path

import pytest

from smo_cli.cli import main


@pytest.mark.skip("Not yet implemented properly")
def test_cluster_sync(runner, mock_smo_env: Path, mock_cluster_service):
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


@pytest.mark.skip("Not yet implemented properly")
def test_cluster_list_no_db(runner, mock_smo_env: Path, mocker):
    """Tests 'smo-cli cluster list' when the DB doesn't exist yet."""
    # We patch the db_session to simulate an error, e.g., db not initialized
    mocker.patch(
        "smo_cli.core.context.CliContext.db_session",
        side_effect=Exception("DB file not found"),
    )

    result = runner.invoke(main, ["cluster", "list"])
    # The main error handler should catch this
    assert "An unexpected error occurred" in result.output
