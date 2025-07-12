from smo_sdk.api.clusters import smo_web_handlers_cluster_get_clusters as clusters_api
from smo_sdk.api.graph import smo_web_handlers_graph_deploy as deploy_api
from smo_sdk.api.graph import smo_web_handlers_graph_get_graph as get_graph_api
from smo_sdk.client import Client
from smo_sdk.models import (
    Cluster,
    Problem,
    SmoWebHandlersGraphDeployJsonBody,
)


def test_client_initialization(sync_client: Client):
    """Tests that the client is initialized correctly."""
    assert str(sync_client.get_httpx_client().base_url) == "http://smo.test/"


def test_get_clusters_success(sync_client, mocked_api, mock_clusters_payload):
    """
    Tests a successful GET /clusters call.
    """
    mocked_api.get("/clusters").respond(200, json=mock_clusters_payload)

    response = clusters_api.sync(client=sync_client)

    assert isinstance(response, list)
    assert len(response) == 2
    assert isinstance(response[0], Cluster)
    assert response[0].name == "cluster-1"


def test_post_request_construction(sync_client, mocked_api):
    """
    Tests that a POST request sends the correct JSON body.
    """
    # Arrange
    request_dict = {"hdaGraph": {"id": "new-graph"}}
    request_body_model = SmoWebHandlersGraphDeployJsonBody.from_dict(request_dict)

    route = mocked_api.post("/project/new-project/graphs").respond(202, text="Accepted")

    deploy_api.sync(client=sync_client, project="new-project", body=request_body_model)

    # Assert
    assert route.called
    last_request = route.calls.last.request
    assert last_request.content == b'{"hdaGraph":{"id":"new-graph"}}'


def test_api_returns_404_error(sync_client, mocked_api):
    """
    Tests that a documented 404 error returns a Problem model, not an exception.
    """
    # Arrange: The problem detail the server would return
    problem_payload = {"title": "Not Found", "status": 404, "detail": "Graph not found"}
    mocked_api.get("/graphs/non-existent-graph").respond(404, json=problem_payload)

    response = get_graph_api.sync(client=sync_client, name="non-existent-graph")

    # Assert that the response is a Problem object with the correct details
    assert isinstance(response, Problem)
    assert response.status == 404
    assert response.title == "Not Found"
