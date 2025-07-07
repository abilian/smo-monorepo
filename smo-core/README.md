# SMO-Core

This package provides the core business logic, database models, and orchestration algorithms for the Synergetic Meta-Orchestrator (SMO).

This is part of the "smo-monorepo" project, and a fork of the original SMO.

## Overview

`smo-core` is a framework-agnostic library designed to be the engine for higher-level applications like a web service (`smo-web`) or a command-line interface (`smo-cli`).

It contains all the necessary components for:

- Managing Hyper Distributed Application Graphs (HDAGs).
- Interacting with Karmada for multi-cluster orchestration.
- Integrating with Prometheus and Grafana for observability.
- Performing intelligent service placement and scaling using CVXPY.

This library is not meant to be run directly. It should be included as a dependency in an application that provides a user interface and a database connection.


## Key Refactoring Changes

(From the original SMO).

1.  **Framework Independence:** All `Flask` and `click` related code has been removed.
2.  **Agnostic Database Setup:** `smo_core/database.py` defines the SQLAlchemy `Base` but leaves the engine and session creation to the consumer application (`smo-web` or `smo-cli`).
3.  **Context-Driven Services:** Service functions in `smo_core/services/` no longer rely on global contexts. They now accept a `context` object (which holds configuration and helper instances) and a `db_session` as arguments. This improves testability and clarity.
4.  **Generic JSON Type:** Models now use `sqlalchemy.types.JSON` with a `postgresql.JSONB` variant to ensure compatibility with both SQLite (for the CLI) and PostgreSQL (for the web app).
5.  **NFVCL Removed:** All code related to the NFVCL integration has been removed.
