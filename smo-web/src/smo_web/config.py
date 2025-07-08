import os
from pathlib import Path

__all__ = ["config"]

# from dotenv import load_dotenv

# dotenv_path = os.environ.get(
#     "DOTENV_PATH", os.path.join(os.path.dirname(__file__), "..", "config", "flask.env")
# )
# if os.path.exists(dotenv_path):
#     load_dotenv(dotenv_path=dotenv_path)

HOME = os.getenv("HOME", "/root")

# Environment variables that must be set
ENV_VARS = {
    "DB_USER": "fermigier",
    "DB_PASSWORD": "",
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "DB_NAME": "smo",
    "SQLALCHEMY_URI": "",
    "KARMADA_KUBECONFIG": "karmada-apiserver.config",
    #
    "GRAFANA_HOST": "http://grafana.orb.local/",
    "GRAFANA_USERNAME": "admin",
    "GRAFANA_PASSWORD": "admin",
    "PROMETHEUS_HOST": "http://127.0.0.1:30090",
    #
    "SCALING_INTERVAL": "30",
    "SCALING_ENABLED": "False",
    "INSECURE_REGISTRY": "True",
}

# Please the static checker
DB_USER = ""
DB_PASSWORD = ""
DB_HOST = ""
DB_PORT = ""
DB_NAME = ""
SQLALCHEMY_URI = ""
KARMADA_KUBECONFIG = ""
GRAFANA_HOST = ""
GRAFANA_USERNAME = ""
GRAFANA_PASSWORD = ""
PROMETHEUS_HOST = ""
INSECURE_REGISTRY = True


def get_boolean(value: str | bool) -> bool:
    """Convert a string to a boolean."""
    match value:
        case bool():
            return value
        case str():
            return value.lower() in ("true", "1", "yes", "y")
        case _:
            raise ValueError(f"Invalid boolean value: {value}")


config = {}

for var_name in ENV_VARS:
    if var_name in os.environ:
        var_value = os.environ[var_name]
    else:
        var_value = ENV_VARS[var_name]

    globals()[var_name] = var_value
    config[var_name] = var_value

if not SQLALCHEMY_URI:
    SQLALCHEMY_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

SMO_CORE_CONFIG = {
    "karmada_kubeconfig": str(Path(HOME) / ".kube" / KARMADA_KUBECONFIG),
    "grafana": {
        "host": GRAFANA_HOST,
        "username": GRAFANA_USERNAME,
        "password": GRAFANA_PASSWORD,
    },
    "prometheus_host": PROMETHEUS_HOST,
    "helm": {
        "insecure_registry": get_boolean(INSECURE_REGISTRY),
    },
}

config["SQLALCHEMY_URI"] = SQLALCHEMY_URI
config["SMO_CORE_CONFIG"] = SMO_CORE_CONFIG
