from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from snoop import snoop

import yaml

DEFAULT_SMO_DIR = Path.home() / ".smo"
CONFIG_FILE = "config.yaml"
DB_FILE = "smo.db"


@dataclass
class Config:
    """Configuration class to manage SMO settings."""

    smo_dir: Path
    config_file: Path
    db_file: Path

    data: dict

    @classmethod
    @snoop
    def load(
        cls, smo_dir: Path | None = None, config_file: Path | None = None
    ) -> Config:
        """Loads the YAML configuration file."""
        if smo_dir is None:
            smo_dir = cls.get_smo_dir()

        if config_file is None:
            config_file = cls.get_config_file()

        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found at {config_file}.")

        with config_file.open() as f:
            data = yaml.safe_load(f)
            return cls(
                smo_dir=smo_dir,
                config_file=config_file,
                db_file=cls.smo_dir / DB_FILE,
                data=data,
            )

    def get(self, *path: list[str]) -> Any:
        value = self.data
        for p in path:
            if p not in self.data:
                raise KeyError(f"Key '{p}' not found in configuration.")
            value = value[p]
        return value

    @classmethod
    def get_smo_dir(cls) -> Path:
        """Returns the SMO directory path."""
        return Path(os.environ.get("SMO_DIR", DEFAULT_SMO_DIR))

    @classmethod
    def get_config_file(cls) -> Path:
        """Returns the path to the configuration file."""
        return cls.get_smo_dir() / CONFIG_FILE

    @classmethod
    def get_db_file(cls) -> Path:
        """Returns the path to the database file."""
        return cls.get_smo_dir() / DB_FILE

    @classmethod
    def create_default_config(cls, config_file: Path | None = None) -> None:
        """Creates a default configuration file."""
        default_config_path = cls.get_config_file()
        default_config_path.parent.mkdir(parents=True, exist_ok=True)
        with default_config_path.open("w") as f:
            yaml.dump(
                default_config_path, f, default_flow_style=False, sort_keys=False
            )

    @classmethod
    def get_default_config(cls) -> dict:
        """Returns the default configuration dictionary."""

        default_config = {
            "smo_dir": str(DEFAULT_SMO_DIR),
            "karmada_kubeconfig": str(
                Path.home() / ".kube" / "karmada-apiserver.config"
            ),
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
        return default_config
