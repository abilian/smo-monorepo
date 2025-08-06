from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

# --- Constants ---
# Use uppercase for constants for better readability.
DEFAULT_SMO_DIR = Path.home() / ".smo"
CONFIG_FILENAME = "config.yaml"
DB_FILENAME = "smo.db"


# --- Main Configuration Class ---


@dataclass
class Config:
    """
    Manages SMO configuration by loading and providing access to settings
    from a YAML file.

    Attributes:
        path (Path): The full path to the loaded configuration file.
        smo_dir (Path): The root directory for SMO data (e.g., ~/.smo).
        db_file (Path): The full path to the SQLite database file.
        data (dict): The raw dictionary of configuration data loaded from the file.
    """

    path: Path
    data: dict = field(repr=False)  # Don't show the full data dict in repr
    smo_dir: Path = field(init=False)
    db_file: Path = field(init=False)

    def __post_init__(self):
        """Set derived path attributes after the object is initialized."""
        self.smo_dir = self.path.parent
        self.db_file = self.smo_dir / DB_FILENAME

    @classmethod
    def load(cls, path: Path | str | None = None) -> Config:
        """
        Loads the configuration from a given path or the default location.

        This is the primary factory method for creating a Config instance.

        Args:
            path: Optional path to the config file. If None, uses the default
                  path determined by get_default_path().

        Returns:
            An instance of the Config class.

        Raises:
            FileNotFoundError: If the configuration file cannot be found.
        """
        if path is None:
            path = cls.get_default_path()

        config_path = Path(path)

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found at {config_path}.")

        with config_path.open("r") as f:
            data = yaml.safe_load(f) or {}

        return cls(path=config_path, data=data)

    def get(self, *path: str, default: Any = None) -> Any:
        """
        Retrieves a nested value from the configuration data.

        Example:
            config.get("grafana", "host", default="http://localhost")

        Args:
            *path: A sequence of keys to traverse the nested dictionary.
            default: The value to return if the key path is not found.

        Returns:
            The requested value, or the default if not found.
        """
        value = self.data
        try:
            for key in path:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    @staticmethod
    def get_smo_dir() -> Path:
        """Returns the SMO directory path, respecting the SMO_DIR env var."""
        return Path(os.environ.get("SMO_DIR", DEFAULT_SMO_DIR))

    @staticmethod
    def get_default_path() -> Path:
        """Returns the default path to the configuration file."""
        return Config.get_smo_dir() / CONFIG_FILENAME

    @staticmethod
    def get_default_db_path() -> Path:
        """Returns the default path to the database file."""
        return Config.get_smo_dir() / DB_FILENAME

    @staticmethod
    def get_default_config_data() -> dict:
        """Returns the default configuration as a dictionary."""
        return {
            "karmada_kubeconfig": str(
                Path.home() / ".kube" / "karmada-apiserver.config"
            ),
            "grafana": {
                "host": "http://localhost:3000",
                "username": "admin",
                "password": "prom-operator",  # A more realistic default
            },
            "prometheus_host": "http://localhost:9090",
            "helm": {
                "insecure_registry": True,
            },
            "scaling": {
                "interval_seconds": 30,
            },
        }

    @staticmethod
    def create_default_config(path: Path | str | None = None) -> None:
        """
        Creates a default configuration file at the given or default path.

        Args:
            path: Optional path to create the file. If None, uses the default.
        """
        if path is None:
            path = Config.get_default_path()

        config_path = Path(path)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        default_data = Config.get_default_config_data()

        with config_path.open("w") as f:
            yaml.dump(default_data, f, default_flow_style=False, sort_keys=False)
