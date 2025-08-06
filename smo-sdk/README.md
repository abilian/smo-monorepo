# Synergetic Meta-Orchestrator (SMO) - Python SDK

This is the official Python SDK for the Synergetic Meta-Orchestrator (SMO) REST API.

This SDK is in part auto-generated from the SMO's [OpenAPI specification](https://gitlab.eclipse.org/eclipse-research-labs/nephele-project/opencall-2/h3ni/smo-monorepo/-/blob/main/smo-web/src/smo_web/swagger/openapi.yaml), ensuring it is always up-to-date and provides complete coverage of the API's features. It provides a simple, pythonic interface that handles all the low-level HTTP requests, data serialization, and error handling for you.

## Core Features

*   **Complete API Coverage**: All API endpoints exposed by the `smo-web` service are available as client methods.
*   **Type-Safe**: Fully type-hinted for an excellent developer experience with autocompletion and static analysis.
*   **Sync and Async Support**: The client can be used in both synchronous and asynchronous (`asyncio`) code, powered by `httpx`.
*   **Pydantic Models**: All request and response bodies are parsed into robust [Pydantic](https://docs.pydantic.dev/) models, providing data validation and an object-oriented interface.
*   **Easy to Maintain**: Can be regenerated with a single command whenever the core SMO API is updated.

## Why Use This SDK?

While it's possible to interact with the SMO REST API using `curl` or a regular HTTP library, this SDK provides significant advantages for any serious development, automation, or testing effort.

### Simplified Application Development and Automation

This SDK make it easy to interact with the SMO with simple Python function or method calls.

*   **No More Manual HTTP:** You don't need to worry about setting headers, serializing JSON bodies, or parsing response data.
*   **IDE Autocompletion:** Because the SDK is fully type-hinted, modern editors will provide autocompletion for API functions and their typed arguments.
*   **Data Validation with Pydantic:** All API responses are automatically parsed into Pydantic models, so you work with objects (`graph.status`, `cluster.name`) instead of dictionaries, preventing typos.
*   **Cleaner Error Handling:** The SDK distinguishes between documented API error responses (which are returned as `Problem` objects) and unexpected network or server errors (which are raised as exceptions).

This makes it the ideal tool for building CI/CD pipeline scripts, custom automation, or higher-level applications on top of the SMO.

### Robust Testing of the SMO Ecosystem

The SDK is the primary tool for writing high-quality integration and end-to-end (E2E) tests for the SMO REST server itself. It provides a clean, stable interface for test scripts to programmatically deploy a graph, poll its status, perform actions, and clean up all resources.

### Architectural Flexibility (Local vs. Remote)

The `smo-cli` tool interacts directly with the `smo-core` Python library. This SDK provides a client-side API that intentionally mirrors the API of the core services. This enables a powerful architectural pattern: code can be written to work with either the local `smo-core` library or the remote REST API with minimal changes, providing ultimate flexibility.

### Long-Term Maintainability

Because this SDK is **auto-generated** directly from the SMO's OpenAPI specification, it acts as a "living client". It will never become stale or fall out of sync with the server's API. When an endpoint is added or a model is changed in the SMO, this SDK can be regenerated with a single command to perfectly reflect the new capabilities.

## Installation

Run `uv sync` from the git repository.

*(Note: This package is not yet published on the PyPI repository.)*

## Getting Started

Using the SDK requires importing the `Client` and the specific API modules you wish to use. The pattern is to pass the initialized `Client` into functions from the API modules.

### Example: Listing Clusters and Deploying a Graph

```python
import httpx

# 1. Import the main client and the specific API modules (with aliases for readability)
from smo_sdk import Client
from smo_sdk.api.clusters import smo_web_handlers_cluster_get_clusters as clusters_api
from smo_sdk.api.graph import (
    smo_web_handlers_graph_deploy as deploy_api,
    smo_web_handlers_graph_get_all_for_project as list_graphs_api,
)
# Import the Pydantic model for the request body
from smo_sdk.models import SmoWebHandlersGraphDeployJsonBody, Problem

# 2. Initialize the client, pointing to your smo-web instance
client = Client(base_url="http://localhost:8000")

# --- List all clusters known to the SMO ---
print("Fetching clusters...")
try:
    clusters_response = clusters_api.sync(client=client)
    if isinstance(clusters_response, list):
        for cluster in clusters_response:
            status = "Ready" if cluster.availability else "Not Ready"
            print(f"  - Cluster: {cluster.name}, CPU: {cluster.available_cpu}, Status: {status}")
    else:
        print(f"  No clusters found or an error occurred: {clusters_response}")
except httpx.RequestError as e:
    print(f"An HTTP error occurred: {e}")


# --- List all graphs within a specific project ---
PROJECT_NAME = "demo1"
print(f"\nFetching graphs for project '{PROJECT_NAME}'...")
graphs_response = list_graphs_api.sync(client=client, project=PROJECT_NAME)
if graphs_response:
    for graph in graphs_response:
        print(f"  - Graph: {graph.name}, Status: {graph.status}")
else:
    print(f"  No graphs found in project '{PROJECT_NAME}'.")


# --- Deploy a new graph from a descriptor ---
print("\nDeploying a new graph...")

# 3. Construct the request body as a dictionary
new_graph_dict = {
    "hdaGraph": {
        "id": "my-sdk-graph",
        "version": "1.0.0",
        "services": [{
            "id": "sdk-service",
            "deployment": {"trigger": {"type": "standard"}, "intent": {"compute": {"cpu": "light"}}},
            "artifact": {"ociImage": "oci://ghcr.io/abilian/hello-world-chart"},
        }],
    }
}

# 4. Create an instance of the Pydantic model from the dictionary
request_body_model = SmoWebHandlersGraphDeployJsonBody.from_dict(new_graph_dict)

deployment_response = deploy_api.sync(client=client, project="sdk-project", body=request_body_model)

# The deploy endpoint returns a Problem model on failure or None on success
if isinstance(deployment_response, Problem):
    print(f"  -> Deployment failed: {deployment_response.detail}")
else:
    print(f"  -> Deployment triggered successfully (Response: {deployment_response}).")

```

## Asynchronous Usage

The SDK provides an identical API for `asyncio` applications. Call the `.asyncio()` variant of the API function and `await` the result.

```python
import asyncio
from smo_sdk import Client
from smo_sdk.api.clusters import smo_web_handlers_cluster_get_clusters as clusters_api

async def main():
    # Initialize the client
    async_client = Client(base_url="http://localhost:8000")

    print("Fetching clusters asynchronously...")
    clusters = await clusters_api.asyncio(client=async_client)

    if isinstance(clusters, list):
        for cluster in clusters:
            print(f"  - Async Cluster: {cluster.name}")

if __name__ == "__main__":
    asyncio.run(main())
```

## SDK Generation & Updates

This library's code is automatically generated by [openapi-python-client](https://github.com/openapi-generators/openapi-python-client).

If the SMO REST API is updated, you can regenerate this SDK to include the changes by running the following command from the root of the repository:

```bash
# Install the generator if you don't have it
# pip install openapi-python-client

# Regenerate the SDK from the SMO's OpenAPI specification
openapi-python-client generate --path /path/to/smo-monorepo/smo-web/src/smo_web/swagger/openapi.yaml --output-path .
```

Please re-run the usual Python code formatters (`isort`, `ruff format`, etc.) after regeneration to ensure the code is properly formatted.

This ensures the SDK remains a perfect, up-to-date reflection of the API's capabilities.

## Development

To set up a development environment:

1.  Clone this repository.
2.  Create and activate a virtual environment, and install the package in editable mode with development dependencies, using `uv`:
    ```bash
    uv sync
    ```
3. Run the test suite:
    ```bash
    uv run pytest
    ```

## License

This project is licensed under the **Apache License 2.0**. See the `LICENSE` file for details.
