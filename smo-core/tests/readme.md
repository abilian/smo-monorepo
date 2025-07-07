# Tests for SMO-Core

## Test Strategy

Since `smo-core` is the engine of the refactored SMO, having a good suite of tests is of paramount importance.

We provide two kinds of tests:

1.  **Unit Tests:** These test individual functions and algorithms in isolation, especially those in the `utils` directory. We use `pytest`'s parameterization to cover various scenarios for placement and intent translation. These tests do not require a database or mocked helpers.

2.  **Integration Tests:** These tests are used to verify the `services` layer. They:
    *   Use an in-memory SQLite database to test database interactions.
    *   Use mocked versions of the `KarmadaHelper`, `PrometheusHelper`, and `GrafanaHelper` to simulate interactions with external systems.
    *   Test the end-to-end logic of a service function (e.g., `deploy_graph`) to ensure it correctly calls helpers, updates the database, and performs its orchestration steps.
