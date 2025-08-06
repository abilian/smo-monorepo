import yaml

CONFIG_PATH = "fastapi1/config.yaml"
DEFAULT_CONFIG_DATA = {
    "database": {"url": "sqlite:///fastapi1/smo.db"},
    "karmada": {"kubeconfig": "~/.kube/karmada.config"},
    "prometheus": {"host": "http://prometheus.monitoring:9090"},
    "grafana": {
        "grafana_host": "http://grafana.monitoring:3000",
        "username": "admin",
        "password": "password",
    },
}

try:
    with open(CONFIG_PATH, "r") as f:
        config_data = yaml.safe_load(f)
except FileNotFoundError:
    print(f"WARNING: Configuration file not found at {CONFIG_PATH}. Using defaults.")
    # A default config, assuming services are running locally or as per README
    config_data = DEFAULT_CONFIG_DATA
