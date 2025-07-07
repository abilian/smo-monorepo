import os
from pathlib import Path

import yaml

DEFAULT_SMO_DIR = Path.home() / ".smo"
CONFIG_FILE = "config.yaml"
DB_FILE = "smo.db"

DEFAULT_CONFIG = {
    "smo_dir": str(DEFAULT_SMO_DIR),
    "karmada_kubeconfig": str(Path.home() / ".kube" / "karmada-apiserver.config"),
    "grafana": {
        "host": "http://localhost:3000",
        # Default Grafana login credentials (for testing purposes only!)
        "username": "admin",
        "password": "admin",
    },
    "prometheus_host": "http://localhost:9090",
    "helm": {
        "insecure_registry": True,
    },
    "scaling": {
        # This interval is used for one-shot queries in the CLI context
        "interval_seconds": 30,
    },
}


def get_smo_dir() -> Path:
    """Returns the SMO directory path."""
    return Path(os.environ.get("SMO_DIR", DEFAULT_SMO_DIR))


def get_config_file() -> Path:
    """Returns the path to the configuration file."""
    return get_smo_dir() / CONFIG_FILE


def get_db_file() -> Path:
    """Returns the path to the database file."""
    return get_smo_dir() / DB_FILE


def get_config(config_file: Path | None = None) -> dict:
    """Loads the YAML configuration file."""
    if config_file is None:
        config_file = get_config_file()
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found at {config_file}.")
    with config_file.open() as f:
        return yaml.safe_load(f)


def create_default_config():
    """Creates a default configuration file."""
    default_config_path = get_config_file()
    default_config_path.parent.mkdir(parents=True, exist_ok=True)
    with default_config_path.open("w") as f:
        yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False, sort_keys=False)
