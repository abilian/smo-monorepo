# SMO Command Line Interface (CLI)

## Overview
The SMO CLI provides terminal-based management of the Synergetic Meta-Orchestrator. It offers a complete interface for deploying and managing Hyper Distributed Application Graphs (HDAGs) across Kubernetes clusters.

## Features

### Core Capabilities
- **Graph Management**: Deploy, start, stop, and remove application graphs
- **Cluster Operations**: View and sync cluster resources and status  
- **Auto-scaling**: Configure and run threshold-based autoscalers
- **Rich Terminal UI**: Colorful, formatted output with tables and panels

### Technical Highlights
- Built with Python 3.8+
- Click framework for CLI commands
- Rich library for terminal formatting  
- SQLite local state storage
- Dishka for dependency injection
- Full integration with smo-core engine

## Installation

```bash
pip install smo-cli
```

## First-Time Setup

1. Initialize configuration:
```bash
smo-cli init
```

2. Edit `~/.smo/config.yaml` to configure:
   - Karmada kubeconfig path
   - Prometheus and Grafana endpoints
   - Helm registry settings

## Usage Examples

### Graph Operations
```bash
# Deploy a graph
smo-cli graph deploy --project my-project graph.yaml

# List graphs
smo-cli graph list

# Describe a graph
smo-cli graph describe my-graph
```

### Cluster Management  
```bash
# Sync cluster info
smo-cli cluster sync

# List clusters
smo-cli cluster list
```

### Auto-scaling
```bash
smo-cli scaler run \
  --target-deployment my-service \
  --up-threshold 50 \
  --down-threshold 10 \
  --up-replicas 5 \
  --down-replicas 1
```

## Requirements
- Python 3.8+
- Kubernetes clusters managed by Karmada
- Prometheus for metrics
- Grafana for dashboards
- Helm and hdarctl in PATH

## Development

### Building and Testing
```bash
# Install with dev dependencies
pip install -e .[dev]

# Run all checks (lint + test)
make all

# Run tests
make test

# Run linters
make lint

# Format code
make format

# Clean build artifacts
make clean
```

### CI/CD Features
- Automated linting with ruff
- Unit and integration tests via pytest
- Code formatting with ruff format
- Virtualenv management with nox

## Roadmap
- Interactive mode with autocomplete
- Bulk operations
- Plugin system
- Enhanced metrics reporting
