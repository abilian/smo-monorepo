import pytest
import respx

from smo_sdk import Client

# --- Constants ---
BASE_URL = "http://smo.test/"


# --- Fixtures ---


@pytest.fixture
def sync_client() -> Client:
    """Provides a synchronous SDK client for testing."""
    return Client(base_url=BASE_URL)


@pytest.fixture
def mocked_api():
    """A fixture to mock the API routes using respx."""
    with respx.mock(base_url=BASE_URL) as mock:
        yield mock


@pytest.fixture
def mock_clusters_payload():
    """Provides a valid JSON payload for a GET /clusters response."""
    return [
        {
            "id": 1,
            "name": "cluster-1",
            "location": "us-east-1",
            "available_cpu": 12.0,
            "available_ram": "48.00 GiB",
            "availability": True,
            "acceleration": True,
            "grafana": "http://grafana.test/d/cluster-1",
        },
        {
            "id": 2,
            "name": "cluster-2",
            "location": "eu-west-1",
            "available_cpu": 20.0,
            "available_ram": "90.00 GiB",
            "availability": False,
            "acceleration": False,
            "grafana": "http://grafana.test/d/cluster-2",
        },
    ]


@pytest.fixture
def mock_graph_payload():
    """Provides a valid JSON payload for a single graph response."""
    return {
        "name": "test-graph",
        "status": "Running",
        "project": "test-project",
        "grafana": "http://grafana.test/d/test-graph",
        "hdaGraph": {"id": "test-graph", "services": []},
        "placement": {},
        "services": [
            {
                "name": "service-a",
                "status": "Deployed",
                "grafana": "http://grafana.test/d/service-a",
                "cluster_affinity": "cluster-1",
                "cpu": "0.5",
                "memory": "500MiB",
                "storage": "10GB",
                "gpu": "0",
                "values_overwrite": {},
                "alert": {},
                "artifact_ref": "oci://example/service-a",
                "artifact_type": "App",
                "artifact_implementer": "Helm",
            }
        ],
    }
