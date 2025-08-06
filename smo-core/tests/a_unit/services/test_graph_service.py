from unittest.mock import MagicMock, patch

import pytest

from smo_core.models import Cluster, Graph, Service
from smo_core.services.graph_service import GraphService


@pytest.fixture
def mock_db_session():
    session = MagicMock()
    session.query.return_value.filter_by.return_value.all.return_value = []
    session.add = MagicMock()  # Ensure add is properly mocked
    return session


@pytest.fixture
def mock_karmada_helper():
    helper = MagicMock()
    helper.get_replicas.return_value = 1
    return helper


@pytest.fixture
def mock_grafana_helper():
    helper = MagicMock()
    helper.publish_dashboard.return_value = {"url": "/d/test"}
    return helper


@pytest.fixture
def mock_prom_helper():
    helper = MagicMock()
    return helper


@pytest.fixture
def sample_graph_descriptor():
    return {
        "id": "test-graph",
        "services": [
            {
                "id": "test-service",
                "artifact": {
                    "ociImage": "test-image",
                    "ociConfig": {"implementer": "test", "type": "test"},
                    "valuesOverwrite": {},
                },
                "deployment": {
                    "intent": {
                        "compute": {
                            "cpu": "small",
                            "ram": "small",
                            "storage": "small",
                            "gpu": {"enabled": "False"},
                        }
                    },
                    "trigger": {},
                },
            }
        ],
    }


def test_fetch_project_graphs(mock_db_session):
    # Setup test data
    graph = Graph(name="test-graph", project="test-project", status="Running")
    mock_db_session.query.return_value.filter_by.return_value.all.return_value = [graph]

    # Create service
    service = GraphService(
        db_session=mock_db_session,
        karmada_helper=MagicMock(),
        grafana_helper=MagicMock(),
        prom_helper=MagicMock(),
        config={},
    )

    # Test
    result = service.fetch_project_graphs("test-project")
    assert len(result) == 1
    assert result[0]["name"] == "test-graph"


def test_fetch_graph(mock_db_session):
    # Setup test data
    graph = Graph(name="test-graph", project="test-project", status="Running")
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = graph

    # Create service
    service = GraphService(
        db_session=mock_db_session,
        karmada_helper=MagicMock(),
        grafana_helper=MagicMock(),
        prom_helper=MagicMock(),
        config={},
    )

    # Test
    result = service.fetch_graph("test-graph")
    assert result.name == "test-graph"


def test_deploy_graph_new_graph(
    mock_db_session,
    mock_karmada_helper,
    mock_grafana_helper,
    mock_prom_helper,
    sample_graph_descriptor,
):
    # Setup mocks
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = None
    mock_db_session.query.return_value.filter_by.return_value.all.return_value = [
        Cluster(
            name="cluster1",
            available_cpu=10.0,
            available_ram="16GiB",
            availability=True,
            acceleration=False,
        )
    ]

    # Create service
    service = GraphService(
        db_session=mock_db_session,
        karmada_helper=mock_karmada_helper,
        grafana_helper=mock_grafana_helper,
        prom_helper=mock_prom_helper,
        config={
            "grafana": {"host": "http://grafana"},
            "karmada_kubeconfig": "/tmp/kubeconfig",
            "helm": {"insecure_registry": False},
        },
    )

    # Test
    service.deploy_graph("test-project", sample_graph_descriptor)

    # Verify
    mock_db_session.add.assert_called()
    mock_db_session.commit.assert_called()
    mock_grafana_helper.publish_dashboard.assert_called()


def test_start_graph(mock_db_session, mock_karmada_helper, mock_prom_helper):
    # Setup test graph with stopped service
    graph = Graph(name="test-graph", status="Stopped")
    service = Service(
        name="test-service",
        status="Not deployed",
        artifact_ref="test-image",
        values_overwrite={
            "clustersAffinity": ["cluster1"],
            "serviceImportClusters": [],
            "namespace": "test-project",
            "serviceAccount": "default",
            "imagePullPolicy": "IfNotPresent",
            "replicaCount": 1,
            "image": {
                "repository": "test-image",
                "pullPolicy": "IfNotPresent",
                "tag": "latest",
            },
            "service": {"type": "ClusterIP", "port": 8080},
            "karmada_kubeconfig": "/tmp/kubeconfig",
            "helm": {"insecure_registry": False},
        },
        artifact_implementer="test",
        artifact_type="test",
        cpu=1.0,
        memory="1GiB",
        storage="10GB",
        gpu=0,
        cluster_affinity="cluster1",
        graph_id=1,
    )
    graph.services = [service]
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = graph

    # Create service
    service = GraphService(
        db_session=mock_db_session,
        karmada_helper=mock_karmada_helper,
        grafana_helper=MagicMock(),
        prom_helper=mock_prom_helper,
        config={
            "karmada_kubeconfig": "/tmp/kubeconfig",
            "helm": {"insecure_registry": False},
        },
    )

    # Test
    service.start_graph("test-graph")

    # Verify
    assert graph.status == "Running"
    # Verify service status was updated
    assert graph.services[0].status == "Deployed"
    mock_db_session.commit.assert_called()


def test_stop_graph(mock_db_session, mock_karmada_helper, mock_prom_helper):
    # Setup test graph with running service
    graph = Graph(name="test-graph", status="Running", project="test-project")
    service = Service(name="test-service", status="Deployed")
    graph.services = [service]
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = graph

    # Create service
    service = GraphService(
        db_session=mock_db_session,
        karmada_helper=mock_karmada_helper,
        grafana_helper=MagicMock(),
        prom_helper=mock_prom_helper,
        config={
            "karmada_kubeconfig": "/tmp/kubeconfig",
            "helm": {"insecure_registry": False},
        },
    )

    # Test
    service.stop_graph("test-graph")

    # Verify
    assert graph.status == "Stopped"
    assert graph.services[0].status == "Not deployed"
    mock_db_session.commit.assert_called()


def test_remove_graph(mock_db_session, mock_karmada_helper, mock_prom_helper):
    # Setup test graph
    graph = Graph(name="test-graph", status="Running")
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = graph

    # Create service
    service = GraphService(
        db_session=mock_db_session,
        karmada_helper=mock_karmada_helper,
        grafana_helper=MagicMock(),
        prom_helper=mock_prom_helper,
        config={"karmada_kubeconfig": "/tmp/kubeconfig"},
    )

    # Test
    service.remove_graph("test-graph")

    # Verify
    mock_db_session.delete.assert_called_with(graph)
    mock_db_session.commit.assert_called()


def test_helm_install_artifact(mock_db_session, mock_karmada_helper):
    """Test the helm install artifact method."""
    service = GraphService(
        db_session=mock_db_session,
        karmada_helper=mock_karmada_helper,
        grafana_helper=MagicMock(),
        prom_helper=MagicMock(),
        config={
            "karmada_kubeconfig": "/tmp/kubeconfig",
            "helm": {"insecure_registry": False},
        },
    )

    with (
        patch("tempfile.NamedTemporaryFile") as mock_tempfile,
        patch("smo_core.utils.external_commands.run_helm") as mock_run_helm,
        patch("os.remove") as mock_remove,
    ):
        mock_tempfile.return_value.__enter__.return_value.name = "/tmp/values.yaml"
        mock_run_helm.return_value = ""  # Mock return value

        # Test
        service._helm_install_artifact(
            "test-service", "test-image", {"key": "value"}, "test-namespace", "install"
        )


def test_trigger_placement(mock_db_session, mock_karmada_helper):
    # Setup test graph with services
    graph = Graph(name="test-graph", status="Running")
    service = Service(
        name="test-service",
        cpu=1.0,
        gpu=0,
        cluster_affinity="cluster1",
        values_overwrite={
            "clustersAffinity": ["cluster1"],
            "serviceImportClusters": [],
        },
        artifact_implementer="test",
        artifact_ref="test-image",
        artifact_type="test",
        memory="1GiB",
        storage="10GB",
    )
    graph.services = [service]
    graph.graph_descriptor = {
        "services": [
            {
                "id": "test-service",
                "deployment": {
                    "intent": {
                        "connectionPoints": [],
                        "compute": {
                            "cpu": "small",
                            "ram": "small",
                            "storage": "small",
                            "gpu": {"enabled": "False"},
                        },
                    }
                },
            }
        ]
    }
    graph.placement = [[1]]  # Initialize placement
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = graph

    # Mock cluster data
    cluster = Cluster(name="cluster1", available_cpu=10.0, acceleration=False)
    mock_db_session.query.return_value.filter_by.return_value.all.return_value = [
        cluster
    ]

    # Create service
    service = GraphService(
        db_session=mock_db_session,
        karmada_helper=mock_karmada_helper,
        grafana_helper=MagicMock(),
        prom_helper=MagicMock(),
        config={
            "karmada_kubeconfig": "/tmp/kubeconfig",
            "helm": {"insecure_registry": False},
        },
    )

    # Test
    service.trigger_placement("test-graph")

    # Verify
    assert graph.placement is not None
    mock_db_session.commit.assert_called()
