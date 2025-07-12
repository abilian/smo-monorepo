# Synergetic Meta-Orchestrator (SMO) - Python SDK

[![PyPI version](https://badge.fury.io/py/smo-sdk.svg)](https://badge.fury.io/py/smo-sdk)
[![Build Status](https://gitlab.eclipse.org/eclipse-research-labs/nephele-project/opencall-2/h3ni/smo-sdk/badges/main/pipeline.svg)](https://gitlab.eclipse.org/eclipse-research-labs/nephele-project/opencall-2/h3ni/smo-sdk/-/pipelines)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

This is the official Python SDK for the Synergetic Meta-Orchestrator (SMO) REST API.

This SDK is inpart auto-generated from the SMO's [OpenAPI specification](https://gitlab.eclipse.org/eclipse-research-labs/nephele-project/opencall-2/h3ni/smo-monorepo/-/blob/main/smo-web-connexion/src/smo_web/swagger/openapi.yaml), ensuring it is always up-to-date and provides complete coverage of the API's features. It provides a simple, pythonic interface that handles all the low-level HTTP requests, data serialization, and error handling for you.

## Core Features

*   **Complete API Coverage**: All API endpoints exposed by the `smo-web` service are available as client methods.
*   **Type-Safe**: Fully type-hinted for an excellent developer experience with autocompletion and static analysis (`mypy`).
*   **Sync and Async Support**: The client can be used in both synchronous and asynchronous (`asyncio`) code, powered by `httpx`.
*   **Pydantic Models**: All request and response bodies are parsed into robust [Pydantic](https://docs.pydantic.dev/) models, providing data validation and a great object-oriented interface.
*   **Easy to Maintain**: Can be regenerated with a single command whenever the core SMO API is updated.

## Installation

The package can be installed from PyPI:

```bash
pip install smo-sdk
```

*(Note: This package name is hypothetical and would need to be published first.)*

Alternatively, you can install it directly from the Git repository:

```bash
pip install git+https://gitlab.eclipse.org/eclipse-research-labs/nephele-project/opencall-2/h3ni/smo-sdk.git
```

## Getting Started

Using the SDK is straightforward. First, instantiate the client, then call the methods corresponding to the API endpoints.

### Example: Listing Clusters and Graphs

```python
from smo_sdk import Client
from smo_sdk.models import HdaGraphDescriptor  # Import Pydantic models

# Initialize the client, pointing to your smo-web instance
client = Client(base_url="http://localhost:8000")

# --- 1. List all clusters known to the SMO ---
print("Fetching clusters...")
try:
    clusters_response = client.cluster.get_clusters.sync()
    if clusters_response:
        for cluster in clusters_response:
            print(f"  - Cluster: {cluster.name}, CPU: {cluster.available_cpu}, Status: {'Ready' if cluster.availability else 'Not Ready'}")
    else:
        print("  No clusters found.")
except Exception as e:
    print(f"An error occurred: {e}")


# --- 2. List all graphs within a specific project ---
PROJECT_NAME = "demo1"
print(f"\nFetching graphs for project '{PROJECT_NAME}'...")
try:
    graphs_response = client.graph.get_all_for_project.sync(project=PROJECT_NAME)
    if graphs_response:
        for graph in graphs_response:
            print(f"  - Graph: {graph.name}, Status: {graph.status}")
    else:
        print(f"  No graphs found in project '{PROJECT_NAME}'.")
except Exception as e:
    print(f"An error occurred: {e}")

# --- 3. Deploy a new graph from a descriptor ---
print("\nDeploying a new graph...")

# Construct the request body using a dictionary.
# The SDK will validate it against the HdaGraphDescriptor Pydantic model.
new_graph_body = {
    "hdaGraph": {
        "id": "my-sdk-graph",
        "version": "1.0.0",
        "services": [
            {
                "id": "sdk-service",
                "deployment": {
                    "trigger": {"type": "standard"},
                    "intent": {"compute": {"cpu": "light", "ram": "small", "storage": "small", "gpu": {"enabled": "False"}}},
                },
                "artifact": {
                    "ociImage": "oci://my-registry/my-chart:latest",
                    "ociConfig": {"type": "App", "implementer": "Helm"},
                    "valuesOverwrite": {"replicaCount": 1},
                },
            }
        ],
    }
}

try:
    deployment_response = client.graph.deploy.sync(project="sdk-project", json_body=new_graph_body)
    print(f"  -> API Response: {deployment_response}")
except Exception as e:
    print(f"An error occurred during deployment: {e}")

```

## Asynchronous Usage

The SDK provides an identical API for `asyncio` applications. Simply instantiate an async client and use `await` on the `.asyncio()` method variant.

```python
import asyncio
from smo_sdk import Client

async def main():
    # Initialize the async client
    async_client = Client(base_url="http://localhost:8000")

    print("Fetching clusters asynchronously...")
    clusters = await async_client.cluster.get_clusters.asyncio()
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
openapi-python-client generate --path /path/to/smo-monorepo/smo-web-connexion/src/smo_web/swagger/openapi.yaml --output-path .
```

This ensures the SDK remains a perfect, up-to-date reflection of the API's capabilities.

## Development

To set up a development environment:

1.  Clone this repository.
2.  Create and activate a virtual environment (`python -m venv .venv && source .venv/bin/activate`).
3.  Install the package in editable mode with development dependencies:
    ```bash
    pip install -e ".[dev]"
    ```
4.  Run the test suite:
    ```bash
    pytest
    ```

## License

This project is licensed under the **Apache License 2.0**. See the [LICENSE](LICENSE) file for details.
