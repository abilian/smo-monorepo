# SMO Web UI

The SMO Web UI provides a modern, user-friendly interface for managing and monitoring Hyper Distributed Application Graphs (HDAGs) across multiple Kubernetes clusters.

## Features

- **Dashboard**: Overview of projects, graphs, and cluster status
- **Graph Management**: Deploy, start, stop, and remove graphs
- **Project Organization**: View and organize graphs by project
- **Cluster Monitoring**: See cluster resources and status
- **Real-time Visualization**: Integrated Grafana dashboards
- **Event Log**: Track system events and operations

## Architecture

The SMO-UI is built with:

- **Frontend**:
  - FastAPI for server-side rendering
  - Jinja2 templates with responsive design
  - Custom Web Components for reusable UI elements
  - Static assets served via FastAPI static files

- **Backend**:
  - FastAPI application server
  - Dishka for dependency injection
  - SQLAlchemy for database access
  - Integration with `smo-core` services

More details in [./docs/architecture.md](./docs/architecture.md)

## Development Setup

### Prerequisites

- Python 3.12+
- Node.js (for frontend assets) - Currently not needed.
- `smo-core` package installed

### Installation

```bash
# Install dependencies
uv sync

# Run development server
make run
```

The UI will be available at `http://localhost:8000`

## Configuration

Configuration is managed through `config.yaml` with these key sections:

```yaml
database:
  url: "sqlite:///data/smo.db"  # SQLite or PostgreSQL connection string

karmada:
  kubeconfig: "~/.kube/karmada.config"  # Path to Karmada kubeconfig

prometheus:
  host: "http://prometheus.monitoring:9090"  # Prometheus server URL

grafana:
  grafana_host: "http://grafana.monitoring:3000"  # Grafana server URL
  username: "admin"  # Grafana admin user
  password: "password"  # Grafana admin password
```

## Production Deployment

For production, we recommend:

1. Building the Docker image:
```bash
docker build -t smo-ui:latest .
```

2. Running with proper configuration:
```bash
docker run -p 8000:8000 \
  -v ./config:/app/config \
  -v ~/.kube:/root/.kube \
  smo-ui:latest
```

## Testing

Run the test suite with:
```bash
uv run pytest
```

## Contributing

See the main project README for contribution guidelines. The UI follows these specific conventions:

- All routes use dependency injection via Dishka
- Templates extend `base.html` for consistent layout
- Static assets go in `src/smo_ui/static/`
- Follow FastAPI best practices for route definitions
