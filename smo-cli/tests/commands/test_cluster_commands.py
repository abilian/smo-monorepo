from click.testing import CliRunner

from smo_cli.cli import main
from smo_core.models.cluster import Cluster


def test_cluster_sync(client: CliRunner):
    """Tests 'smo-cli cluster sync' using the default mocked service."""
    result = client.invoke(main, ["-v", "cluster", "sync"])
    assert result.exit_code == 0, result.output
    assert "Successfully synced 2 cluster(s)." in result.output
    assert "cluster-1" in result.output


def test_list_clusters_empty(client: CliRunner, mock_cluster_service):
    """Tests the 'list' command when the service returns an empty list."""
    # Patch the INSTANCE from the DI container, not the class
    mock_cluster_service.list_clusters = lambda: []

    result = client.invoke(main, ["-v", "cluster", "list"])
    assert result.exit_code == 0, result.output
    assert "No clusters found" in result.output


def test_make_table_with_model_objects(client: CliRunner, mock_cluster_service):
    """Ensures the `.to_dict()` branch is covered in the table helper."""
    # Create real model objects to be returned by the mock service
    mock_clusters = [
        Cluster(
            name="model-cluster",
            availability=True,
            location="loc",
            acceleration=False,
            available_cpu=1.0,
            available_ram="1Gi",
        ),
    ]
    mock_cluster_service.list_clusters = lambda: mock_clusters

    result = client.invoke(main, ["-v", "cluster", "list"])
    assert result.exit_code == 0, result.output
    assert "model-cluster" in result.output
