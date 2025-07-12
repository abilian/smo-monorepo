import os
import time
import uuid

import pytest

from smo_sdk import Client
from smo_sdk.api.graph import smo_web_handlers_graph_deploy as deploy_api
from smo_sdk.api.graph import (
    smo_web_handlers_graph_get_all_for_project as get_all_for_project_api,
)
from smo_sdk.api.graph import smo_web_handlers_graph_get_graph as get_graph_api
from smo_sdk.api.graph import smo_web_handlers_graph_remove as remove_api
from smo_sdk.api.graph import smo_web_handlers_graph_start as start_api
from smo_sdk.api.graph import smo_web_handlers_graph_stop as stop_api
from smo_sdk.models import SmoWebHandlersGraphDeployJsonBody

SMO_API_URL = os.environ.get("SMO_API_URL", "http://localhost:8000")
pytestmark = pytest.mark.e2e


@pytest.fixture(scope="module")
def live_client() -> Client:
    return Client(base_url=SMO_API_URL, timeout=30.0)


@pytest.fixture(scope="module")
def e2e_project_name() -> str:
    return f"sdk-e2e-test-project-{uuid.uuid4().hex[:8]}"


@pytest.fixture(scope="module")
def e2e_graph_body() -> SmoWebHandlersGraphDeployJsonBody:
    graph_id = f"e2e-graph-{uuid.uuid4().hex[:6]}"
    return SmoWebHandlersGraphDeployJsonBody.from_dict(
        {
            "hdaGraph": {
                "id": graph_id,
                "version": "1.0.0",
                "services": [
                    {
                        "id": f"{graph_id}-service",
                        "deployment": {"trigger": {"type": "standard"}, "intent": {"compute": {"cpu": "light"}}},
                        "artifact": {"ociImage": "oci://ghcr.io/abilian/hello-world-chart"},
                    }
                ],
            }
        }
    )


@pytest.mark.skip("Needs a live SMO API to run - deactivated for now")
def test_full_graph_lifecycle(
    live_client: Client,
    e2e_project_name: str,
    e2e_graph_body: SmoWebHandlersGraphDeployJsonBody,
):
    graph_id = e2e_graph_body.to_dict()["hdaGraph"]["id"]

    # 1. DEPLOY
    deploy_api.sync(client=live_client, project=e2e_project_name, body=e2e_graph_body)
    time.sleep(15)

    # 2. LIST and VERIFY
    graphs = get_all_for_project_api.sync(client=live_client, project=e2e_project_name)
    assert any(g.name == graph_id for g in graphs)

    # 3. DESCRIBE
    graph_details = get_graph_api.sync(client=live_client, name=graph_id)
    assert graph_details.status == "Running"

    # 4. STOP
    stop_api.sync(client=live_client, name=graph_id)
    time.sleep(10)
    graph_details_after_stop = get_graph_api.sync(client=live_client, name=graph_id)
    assert graph_details_after_stop.status == "Stopped"

    # 5. START
    start_api.sync(client=live_client, name=graph_id)
    time.sleep(15)
    graph_details_after_start = get_graph_api.sync(client=live_client, name=graph_id)
    assert graph_details_after_start.status == "Running"

    # 6. CLEANUP
    remove_api.sync(client=live_client, name=graph_id)
