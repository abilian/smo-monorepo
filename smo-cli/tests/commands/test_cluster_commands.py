from pathlib import Path

import pytest

from smo_cli.cli import main


@pytest.fixture
def mock_cluster_service(mocker):
    """Mocks the ClusterService class from smo_core."""
    return mocker.patch("smo_core.services.cluster_service.ClusterService")


def test_cluster_sync(runner, tmp_smo_dir: Path, mock_cluster_service, mocker):
    """Tests 'smo-cli cluster sync'."""

    # Mock Grafana calls to avoid 401 errors
    mocker.patch(
        "smo_core.helpers.grafana.grafana_helper.GrafanaHelper.publish_dashboard"
    )

    # Configure the mock to return some data
    mock_cluster_service.fetch_clusters.return_value = [
        {
            "name": "kind-host",
            "available_cpu": 6.95,
            "available_ram": "7.33 GiB",
            "availability": True,
            "acceleration": False,
            "location": "Unknown",
        }
    ]

    result = runner.invoke(main, ["cluster", "sync"])
    assert result.exit_code == 0
    assert "kind-host" in result.output
    assert "Successfully synced" in result.output


def test_cluster_list_no_db(runner, tmp_smo_dir: Path, mocker):
    """Tests 'smo-cli cluster list' when the DB doesn't exist yet."""

    # We patch the DbProvider to simulate an empty result
    mocker.patch(
        "smo_cli.providers.DbProvider.get_db_session",
        return_value=[],
    )

    result = runner.invoke(main, ["cluster", "list"])
    assert result.exit_code == 0
    assert "No clusters found" in result.output
