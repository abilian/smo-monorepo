# SMO Monorepo - Technical Notes

This document provides a technical overview the codebase of the Synergetic Meta-Orchestrator (SMO) monorepo. It assumes you have already read the `README.md` files for the top-level project and the individual packages (`smo-core`, `smo-cli`, `smo-web-connexion`).

## 1. The Core-Wrapper Design Pattern

The most important architectural concept is the strict separation between the headless `smo-core` library and the user-facing "wrapper" applications (`smo-cli` and `smo-web-connexion`). This is achieved through a consistent **dependency injection** and **context-passing** pattern.

### `smo-core`: The Headless Engine

- **`SmoCoreContext` (`smo_core/context.py`):** This dataclass is the heart of the dependency injection system. It acts as a container for all state and helper instances (like `KarmadaHelper`, `GrafanaHelper`, etc.) that service functions need to operate.
- **Service Functions (`smo_core/services/`):** Every function in the service layer is designed to be stateless. They receive the `SmoCoreContext` and a `db_session` as arguments. They contain no global state and are entirely unaware of whether they are being called by a CLI or a web request.

### `smo-cli`: The Command-Line Wrapper

The `smo-cli` package demonstrates how a wrapper provides the necessary context to `smo-core`.

- **`CliContext` (`smo_cli/core/context.py`):** This is the CLI's own context object. Its primary job is to load the `~/.smo/config.yaml` file, initialize the helper classes, and assemble the `SmoCoreContext` required by the service layer.
- **`pass_context` Decorator:** This custom decorator is the glue. It automatically creates the `CliContext` instance once and passes it to every command function, abstracting away the boilerplate of context management.
- **Database Management (`smo_cli/core/database.py`):** The CLI is responsible for creating the SQLAlchemy engine for its local `smo.db` SQLite file. The `DbManager` class handles this and provides a session factory.

### `smo-web`: The Web API Wrapper

The web application implements the exact same pattern but adapts it to a web server's request-response lifecycle.

- **Request-Scoped Factories (`smo_web/util.py`):** Instead of a singleton context object like the CLI, the web app uses factory functions:
    - `get_core_context()`: Called at the beginning of a request handler to create a fresh `SmoCoreContext`.
    - `get_db_session()`: Creates a request-scoped database session from the session factory.
- **Handlers (`smo_web/handlers/`):** Each API handler function (e.g., `deploy`, `get_graph`) uses these factory functions to get the context and DB session it needs before calling the corresponding function in `smo_core.services`.

This pattern ensures `smo-core` remains a pure, reusable library, while the wrappers handle the specifics of their environment (local config files vs. environment variables, SQLite vs. PostgreSQL).

## 2. Key Implementation Details in `smo-core`

### Graph Lifecycle (`smo_core/services/hdag/graph_service.py`)

This is the most complex service and orchestrates the entire application lifecycle. A typical `deploy_graph` call follows this sequence:

1.  **Database Persistence:** A new `Graph` record is created in the database to represent the desired state.
2.  **Placement Calculation:** An initial placement is determined. `calculate_naive_placement` is used for the first deployment, which is a greedy algorithm. The more complex, CVXPY-based `decide_placement` is used for re-optimization (`re-place` command).
3.  **Helper Interaction:**
    - The `GrafanaHelper` is called to generate and publish new dashboards for the graph and its individual services.
    - If a service is triggered by an event, the `PrometheusHelper` is called to add a new alert rule to Prometheus.
4.  **External Command Execution:** The `run_helm` utility is called via a `subprocess` to execute `helm install` or `helm upgrade`, passing in the artifact URL and any dynamically generated `valuesOverwrite` configuration.

### Optimization Logic (`smo_core/utils/`)

The "intelligence" of the SMO resides in the `placement.py` and `scaling.py` modules.

- **`placement.py`:** `decide_placement` formulates the placement problem as a boolean integer programming problem. It uses `cvxpy` to define decision variables (`x` for placement), an objective function (minimizing deployment and re-optimization costs), and constraints (cluster capacity, feature requirements).
- **`scaling.py`:** `decide_replicas` similarly uses `cvxpy`. It defines an objective function to minimize resource utilization (`w_util`) and transitional costs (`w_trans`, i.e., the cost of changing the replica count), subject to constraints like CPU capacity and the service's ability to handle the current request rate.

### Database Abstraction (`smo_core/models/`)

A notable implementation detail is the use of a generic JSON type to support multiple database backends:

```python
# From smo_core/models/hdag/graph.py
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON

JsonType = JSON().with_variant(JSONB, "postgresql")
```

This code defines a type that uses the standard `JSON` type by default (which works with SQLite's text-based JSON support) but automatically switches to the more efficient binary `JSONB` type when the application is connected to a PostgreSQL database.

The practical benefit of this approach is to be able to develop / debug the SMO without needing a PostgreSQL instance, while still being able to deploy to production with PostgreSQL without changing the codebase.

## 3. Interacting with the Outside World

The SMO needs to control several external systems. The implementation of these interactions is straightforward and isolated within specific modules.

- **Kubernetes/Karmada:** All interactions are handled by `KarmadaHelper` (`smo_core/helpers/karmada_helper.py`), which is a lightweight wrapper around the official `kubernetes` Python client library. It uses the `CustomObjectsApi` to fetch cluster status and the `AppsV1Api` to manage deployments (e.g., scaling).
- **External CLIs (`hdarctl`, `helm`):** To avoid re-implementing complex logic like pulling OCI artifacts or managing Helm releases, the SMO invokes these tools directly as command-line programs. The `smo_core/utils/external_commands.py` module contains simple `subprocess.run` wrappers for this purpose. This approach leverages existing, robust tooling.
- **Observability Stack:**
    - `GrafanaHelper` communicates with Grafana's REST API to programmatically publish JSON dashboard models.
    - `PrometheusHelper` uses a `requests` client to query the Prometheus API for metrics and, critically, uses the Kubernetes API to modify the `PrometheusRule` custom resource to dynamically manage alerting rules.

## 4. API and CLI Implementation

- **`smo-web`'s Single Source of Truth:** The behavior of the web API is dictated entirely by `smo-web/swagger/openapi.yaml`. The Connexion framework uses this file to handle routing, request validation, response validation, and generation of the interactive Swagger UI. The Python handler code is simply the implementation logic that fulfills the contract defined in the OpenAPI spec.
- **`smo-cli`'s Rich Output:** The CLI uses the `rich` library extensively to provide a modern user experience with formatted tables, colors, and panels. The `show_clusters` and `show_graphs` functions in the command modules are responsible for taking the data returned by the core services and rendering it for the console.
