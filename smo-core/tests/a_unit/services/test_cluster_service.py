from unittest.mock import MagicMock, create_autospec

import pytest

from smo_core.models.cluster import Cluster
from smo_core.services.cluster_service import ClusterService


@pytest.fixture
def mock_db_session():
    session = MagicMock()
    session.scalars.return_value.all.return_value = []
    return session


@pytest.fixture
def mock_karmada_helper():
    helper = MagicMock()
    helper.get_cluster_info.return_value = {
        "cluster1": {
            "remaining_cpu": 10.0,
            "remaining_memory_bytes": "10.00 GiB",
            "availability": True,
        }
    }
    return helper


@pytest.fixture
def mock_grafana_helper():
    helper = MagicMock()
    helper.create_cluster_dashboard.return_value = {"dashboard": {"uid": "test"}}
    helper.publish_dashboard.return_value = {"url": "/d/test"}
    return helper


def test_list_clusters(mock_db_session):
    # Setup test data
    cluster = Cluster(
        name="test-cluster", available_cpu=4.0, available_ram="16GiB", availability=True
    )
    mock_db_session.scalars.return_value.all.return_value = [cluster]

    # Create service
    service = ClusterService(
        db_session=mock_db_session,
        karmada_helper=MagicMock(),
        grafana_helper=MagicMock(),
        config={},
    )

    # Test
    result = service.list_clusters()
    assert len(result) == 1
    assert result[0].name == "test-cluster"


def test_fetch_clusters_new_cluster(
    mock_db_session, mock_karmada_helper, mock_grafana_helper
):
    # Setup mock cluster object
    mock_cluster = MagicMock()
    mock_cluster.to_dict.return_value = {
        "name": "cluster1",
        "available_cpu": 10.0,
        "available_ram": "10.00 GiB",
        "availability": True,
    }
    mock_db_session.scalars.return_value.first.return_value = (
        None  # No existing cluster
    )
    mock_db_session.add.return_value = mock_cluster

    # Setup service
    service = ClusterService(
        db_session=mock_db_session,
        karmada_helper=mock_karmada_helper,
        grafana_helper=mock_grafana_helper,
        config={"grafana": {"host": "http://grafana"}},
    )

    # Test
    result = service.fetch_clusters()
    assert len(result) == 1
    assert result[0]["name"] == "cluster1"
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()


def test_fetch_clusters_existing_cluster(
    mock_db_session, mock_karmada_helper, mock_grafana_helper
):
    # Setup existing cluster
    existing_cluster = Cluster(
        name="cluster1", available_cpu=5.0, available_ram="5.00 GiB", availability=False
    )
    mock_db_session.scalars.return_value.first.return_value = existing_cluster

    # Setup service
    service = ClusterService(
        db_session=mock_db_session,
        karmada_helper=mock_karmada_helper,
        grafana_helper=mock_grafana_helper,
        config={"grafana": {"host": "http://grafana"}},
    )

    # Test
    result = service.fetch_clusters()
    assert len(result) == 1
    assert result[0]["available_cpu"] == 10.0  # Updated from mock
    mock_db_session.add.assert_not_called()  # Shouldn't add existing cluster
