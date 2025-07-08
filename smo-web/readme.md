# SMO-Web

This package provides a modern, API-first REST interface for the Synergetic Meta-Orchestrator (SMO), built with Connexion 3 and powered by the `smo-core` library.

## Overview

This application serves as an ASGI web front-end for the SMO engine. It uses an `openapi.yaml` specification as the single source of truth for the API, providing automatic routing, request/response validation, and interactive documentation out of the box.

It is designed to be run as a containerized web service that connects to a PostgreSQL database for state management.

### Key Features

-   **API-First Design**: The `openapi.yaml` file drives the application's behavior, ensuring the implementation always matches the specification.
-   **Automatic Validation**: Connexion automatically validates incoming request bodies, parameters, and response data against the OpenAPI spec.
-   **Interactive Documentation**: A Swagger UI is automatically generated and served, providing live, interactive API documentation.
-   **ASGI Native**: Built on the modern ASGI standard for high-performance, asynchronous web serving.
-   **Modular Architecture**: Fully decoupled from the core orchestration logic, which is provided by the `smo-core` library.

## Architecture

This package is the web layer of the SMO ecosystem. It does not contain the primary business logic itself. The operational flow is as follows:

1.  A user or client sends an HTTP request to an endpoint on this `smo-web` application.
2.  Connexion validates and routes the request to the appropriate handler function in `smo_web/handlers/`.
3.  The handler function creates a context and calls a service function from the `smo-core` library, passing the necessary parameters.
4.  The `smo-core` library executes the complex orchestration logic (interacting with Karmada, Prometheus, etc.).
5.  The result is returned to the handler, which then sends the HTTP response back to the client.

## Prerequisites

Before running this application, ensure you have the following components set up and accessible:

-   Python 3.12+
-   A running **PostgreSQL** (or **SQLite**, for development) database.
-   The `smo-core` package installed and available in your Python environment.
-   A running **Karmada** control plane.
-   Access to other required infrastructure (Prometheus, Grafana, OCI Registry).

## Installation

```bash
uv sync
. .venv/bin/activate # or activate.csh / activate.fish / etc.
```

## Configuration

The application is configured using environment variables, which can be placed in a `.env` file for convenience.

Check the `src/smo_web/config.py` for a list of env variables that can be set.

## Running the Application

This is an ASGI application and must be run with a compatible server.

### 1. Development (with Uvicorn)

Uvicorn is a lightning-fast ASGI server, perfect for local development. The `--reload` flag will automatically restart the server when you make changes to the code.

```bash
uvicorn smo_web.app:connexion_app --host 0.0.0.0 --port 8000 --reload
```
*   `smo_web.app:connexion_app` refers to the `connexion_app` instance inside the `smo_web/app.py` module.

### 2. Production (with Gunicorn)

Gunicorn is a battle-tested process manager. To run an ASGI application like this, you must use an ASGI-compliant worker class, such as `uvicorn.workers.UvicornWorker`.

```bash
gunicorn \
    -k uvicorn.workers.UvicornWorker \
    --workers 4 \
    --bind 0.0.0.0:8000 \
    smo_web.app:connexion_app
```
*   `-k uvicorn.workers.UvicornWorker`: This tells Gunicorn to use Uvicorn's worker class to handle requests.
*   `--workers 4`: A common starting point is `(2 * <number_of_cpu_cores>) + 1`. Adjust based on your server's resources.

### 3. High-Performance Alternative (with Granian)

Granian is a modern, high-performance ASGI server written in Rust. It can offer significant performance benefits.

```bash
granian --interface asgi --host 0.0.0.0 --port 8000 smo_web.app:connexion_app
```

(Assuming Granian is available).

### 4. Running with Docker (Recommended)

The most robust way to run the application and its database is with Docker Compose.

```bash
docker compose up --build -d
```

## API Documentation

Once the application is running, the interactive Swagger UI is available at:

[**http://localhost:8000/ui/**](http://localhost:8000/ui/)

You can use this interface to explore all available API endpoints, view their schemas, and execute requests directly from your browser.

## Running Tests

To run the test suite, first install the test dependencies and then use `pytest`.

```bash
pytest
# Or
make test
```
