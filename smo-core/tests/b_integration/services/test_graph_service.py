import pytest

from smo_core.models.cluster import Cluster
from smo_core.models.hdag.graph import Graph
from smo_core.models.hdag.service import Service
from smo_core.services import cluster_service
from smo_core.services.hdag import graph_service

# A sample graph descriptor for testing
TEST_GRAPH_DESCRIPTOR = {
    "id": "my-test-graph",
    "version": "1.0.0",
    "hdaGraphIntent": {"useStaticPlacement": False},
    "services": [
        {
            "id": "service-a",
            "deployment": {
                "trigger": {"type": "standard"},
                "intent": {
                    "compute": {
                        "cpu": "light",
                        "ram": "small",
                        "storage": "small",
                        "gpu": {"enabled": "False"},
                    },
                    "connectionPoints": ["service-b"],
                },
            },
            "artifact": {
                "ociImage": "oci://example.com/service-a",
                "ociConfig": {"type": "App", "implementer": "Helm"},
                "valuesOverwrite": {},
            },
        },
        {
            "id": "service-b",
            "deployment": {
                "trigger": {"type": "standard"},
                "intent": {
                    "compute": {
                        "cpu": "small",
                        "ram": "small",
                        "storage": "small",
                        "gpu": {"enabled": "True"},
                    }
                },
            },
            "artifact": {
                "ociImage": "oci://example.com/service-b",
                "ociConfig": {"type": "App", "implementer": "Helm"},
                "valuesOverwrite": {},
            },
        },
        {
            "id": "service-c-conditional",
            "deployment": {
                "trigger": {
                    "event": {
                        "events": [
                            {
                                "id": "high-load",
                                "condition": {
                                    "promQuery": "some_metric > 100",
                                    "gracePeriod": "1m",
                                    "description": "High load alert",
                                },
                            }
                        ]
                    }
                },
                "intent": {
                    "compute": {
                        "cpu": "small",
                        "ram": "small",
                        "storage": "small",
                        "gpu": {"enabled": "False"},
                    }
                },
            },
            "artifact": {
                "ociImage": "oci://example.com/service-c",
                "ociConfig": {"type": "App", "implementer": "Helm"},
                "valuesOverwrite": {},
            },
        },
    ],
}


@pytest.fixture
def populated_db_session(db_session):
    """A db session with clusters already populated."""
    # Create some mock clusters
    db_session.add(
        Cluster(
            name="cluster-1",
            available_cpu=12.0,
            available_ram="48.00 GiB",
            availability=True,
            acceleration=True,
        )
    )
    db_session.add(
        Cluster(
            name="cluster-2",
            available_cpu=22.0,
            available_ram="98.00 GiB",
            availability=True,
            acceleration=False,
        )
    )
    db_session.commit()
    return db_session


def test_deploy_graph(mock_context, populated_db_session):
    """Test the full graph deployment service function."""
    project = "test-project"

    # Call the service function
    graph_service.deploy_graph(
        mock_context, populated_db_session, project, TEST_GRAPH_DESCRIPTOR
    )

    # --- Assertions ---

    # 1. Check database state
    graph = populated_db_session.query(Graph).filter_by(name="my-test-graph").one()
    assert graph is not None
    assert graph.project == project
    assert graph.status == "Running"
    assert len(graph.services) == 3

    # 2. Check service details and placement
    service_a = populated_db_session.query(Service).filter_by(name="service-a").one()
    service_b = populated_db_session.query(Service).filter_by(name="service-b").one()
    service_c = (
        populated_db_session.query(Service)
        .filter_by(name="service-c-conditional")
        .one()
    )

    # Service B needs GPU, so it must be on cluster-1
    assert service_b.cluster_affinity == "cluster-1"
    # Service A has no GPU need, so it could be on either. Naive placement puts it on cluster-1 first.
    assert service_a.cluster_affinity == "cluster-1"

    # 3. Check service status (conditional vs. standard)
    assert service_a.status == "Deployed"
    assert service_b.status == "Deployed"
    assert service_c.status == "Pending"  # Because it's conditional

    # 4. Check that Prometheus helper was called for the conditional alert
    assert mock_context.prometheus.update_alert_rules.call_count == 1
    mock_context.prometheus.update_alert_rules.assert_called_once_with(
        mock_context,
        {
            "alert": "high-load",
            "annotations": {
                "description": "High load alert",
                "summary": "High load alert",
            },
            "expr": "some_metric > 100",
            "for": "1m",
            "labels": {"severity": "critical", "service": "service-c-conditional"},
        },
        "add",
    )

    # 5. Check helm values for service imports
    # service-a connects to service-b. service-b is on cluster-1. So service-b's service
    # needs to be imported to cluster-1 (where service-a is).
    vo_a = service_a.values_overwrite
    assert vo_a["clustersAffinity"] == ["cluster-1"]

    vo_b = service_b.values_overwrite
    assert vo_b["clustersAffinity"] == ["cluster-1"]
    assert vo_b["serviceImportClusters"] == [
        "cluster-1"
    ]  # Imported for service-a to use


def test_remove_graph(mock_context, populated_db_session):
    """Test removing a graph."""
    project = "test-project"

    # First, deploy the graph
    graph_service.deploy_graph(
        mock_context, populated_db_session, project, TEST_GRAPH_DESCRIPTOR
    )

    # Ensure it's there
    graph = (
        populated_db_session.query(Graph).filter_by(name="my-test-graph").one_or_none()
    )
    assert graph is not None

    # Now, remove it
    graph_service.remove_graph(mock_context, populated_db_session, "my-test-graph")

    # Check that it's gone
    graph_after_delete = (
        populated_db_session.query(Graph).filter_by(name="my-test-graph").one_or_none()
    )
    assert graph_after_delete is None

    # Check that the alert removal was called for the conditional service
    mock_context.prometheus.update_alert_rules.assert_called_with(
        mock_context,
        # The second call is the removal
        {
            "alert": "high-load",
            "annotations": {
                "description": "High load alert",
                "summary": "High load alert",
            },
            "expr": "some_metric > 100",
            "for": "1m",
            "labels": {"severity": "critical", "service": "service-c-conditional"},
        },
        "remove",
    )
