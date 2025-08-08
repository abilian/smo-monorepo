from dataclasses import dataclass

import yaml

CONFIG_PATH = "config.yaml"
DEFAULT_CONFIG_DATA = {
    "database": {
        "url": "sqlite:///data/smo.db",
    },
    "karmada": {"kubeconfig": "~/.kube/karmada.config"},
    "prometheus": {"host": "http://prometheus.monitoring:9090"},
    "grafana": {
        "grafana_host": "http://grafana.monitoring:3000",
        "username": "admin",
        "password": "password",
    },
}

try:
    with open(CONFIG_PATH) as f:
        config_data = yaml.safe_load(f)
except FileNotFoundError:
    print(f"WARNING: Configuration file not found at {CONFIG_PATH}. Using defaults.")
    # A default config, assuming services are running locally or as per README
    config_data = DEFAULT_CONFIG_DATA


@dataclass(frozen=True)
class Config:
    _data: dict

    def get(self, path: str, default=None):
        """
        Retrieves a value from the configuration data using a list of keys.

        Args:
            path (list[str]): A list of keys to traverse the nested dictionary.
            default: The value to return if the key path is not found.
        Returns:
            The requested value, or the default if not found.
        """
        value = self._data
        path_list = path.split(".")
        try:
            for key in path_list:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    @property
    def data(self):
        return self._data


config = Config(_data=config_data)
