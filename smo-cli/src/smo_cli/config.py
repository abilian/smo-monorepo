from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

DEFAULT_SMO_DIR = Path.home() / ".smo"
CONFIG_FILENAME = "config.yaml"
DB_FILENAME = "smo.db"


class BaseConfig:
    """
    Manages SMO configuration by loading and providing access to settings
    from a YAML file.

    Attributes:
        path (Path): The full path to the loaded configuration file.
        data (dict): The raw dictionary of configuration data loaded from the file.
    """

    path: Path | None
    data: dict | None

    @classmethod
    def load(cls, path: Path | str | None = None) -> BaseConfig:
        """
        Loads the configuration from a given path or the default location.

        This is the primary factory method for creating a Config instance.

        Args:
            path: Optional path to the config file. If None, uses the default
                  path determined by get_default_path().

        Returns:
            An instance of the Config class.
        """
        if path is None:
            path = cls.get_default_path()

        config_path = Path(path)

        if not config_path.exists():
            return DefaultConfig()

        with config_path.open("r") as f:
            data = yaml.safe_load(f) or {}

        return Config(path=config_path, data=data)

    @staticmethod
    def get_smo_dir() -> Path:
        """Returns the SMO directory path, respecting the SMO_DIR env var."""
        return Path(os.environ.get("SMO_DIR", DEFAULT_SMO_DIR)).expanduser()

    @property
    def smo_dir(self) -> Path:
        """Returns the SMO directory path for this config instance."""
        return self.get_smo_dir()

    @staticmethod
    def get_default_path() -> Path:
        """Returns the default path to the configuration file."""
        return Config.get_smo_dir() / CONFIG_FILENAME

    def get(self, path: str, default: Any = None) -> Any:
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
        path_list = path.split(".")
        try:
            for key in path_list:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default


@dataclass
class Config(BaseConfig):
    path: Path | None = None
    data: dict = field(default_factory=dict, repr=False)


class DefaultConfig(BaseConfig):
    """
    A default configuration instance that is loaded at module import time.
    This allows other parts of the application to access the default config
    without needing to call Config.load() explicitly.
    """

    path = None

    @property
    def data(self) -> dict:
        """Returns the default configuration as a dictionary."""
        db_path = self.get_smo_dir() / DB_FILENAME
        return {
            "db": {
                "url": "sqlite:///" + str(db_path),
            },
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

    def write_default_config(self, path: Path | str | None = None) -> None:
        """
        Creates a default configuration file at the given or default path.

        Args:
            path: Optional path to create the file. If None, uses the default.
        """
        if path is None:
            path = self.get_default_path()

        config_path = Path(path)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with config_path.open("w") as f:
            yaml.dump(self.data, f, default_flow_style=False, sort_keys=False)
