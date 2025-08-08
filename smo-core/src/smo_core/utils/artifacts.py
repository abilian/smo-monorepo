import tempfile
from pathlib import Path

import yaml

from smo_core.utils import run_hdarctl


def get_graph_from_artifact(artifact_ref: str) -> dict:
    """Fetches a graph descriptor from an artifact reference."""
    with tempfile.TemporaryDirectory() as dirpath:
        print(f"Pulling artifact {artifact_ref}...")
        result = run_hdarctl("pull", artifact_ref, "--untar", "--destination", dirpath)
        print(result)

        for yaml_file_path in Path(dirpath).rglob("*.yml"):
            with open(yaml_file_path) as yaml_file:
                return yaml.safe_load(yaml_file)

        for yaml_file_path in Path(dirpath).rglob("*.yaml"):
            with open(yaml_file_path) as yaml_file:
                return yaml.safe_load(yaml_file)

    raise FileNotFoundError("No YAML descriptor found in artifact.")
