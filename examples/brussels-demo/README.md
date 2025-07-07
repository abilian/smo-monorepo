# Brussels Demo (refactored for the SMO Mononorepo and CLI)

This project contains an image detection graph designed for deployment on a Hyper-Distributed Application-aware platform.

It uses **Python Invoke** for task automation.

## Prerequisites

Before you begin, ensure you have the following tools installed:

1.  Python 3, `uv` and `invoke`.

Just run `uv sync` and you should be good.

2. **The SMO testbed**: Must be running and configured.

3. **hdarctl** and **helm**: The command-line tools for managing Hyper-Distributed Application artifacts. The version used for this project can be found [here](https://gitlab.eclipse.org/eclipse-research-labs/nephele-project/nephele-development-sandbox/-/raw/main/tools/hdarctl). Make sure it's in your system's `PATH`. Same for `helm`.

## Configuration

### ⚠️ Important
All configuration is handled at the top of the `tasks.py` file. Before running any tasks, open `tasks.py` and set the `HOST_IP` variable to your host machine's IP address.

```python
# tasks.py

# --- Configuration ---
HOST_IP = os.environ.get("HOST_IP", "127.0.0.1") # <-- CHANGE THIS
REGISTRY = f"{HOST_IP}:5000"
# ...
```

Alternatively, you can set it as an environment variable: `export HOST_IP=192.168.1.100`.


## Project Layout

```
├── hdag/
├── image-compression-vo/
├── image-detection/
├── noise-reduction/
├── src/
├── create-existing-artifact.sh
├── tasks.py
└── README.md
```

-   **hdag**: Contains the Hyper-Distributed Application Graph (HDAG) descriptor.
-   **image-compression-vo**: Helm chart for the image compression Virtual Object (VO).
-   **image-detection**: Helm chart for the image detection application.
-   **noise-reduction**: Helm chart for the noise reduction application.
-   **src**: Source code for the Docker images of each application.
-   **create-existing-artifact.sh**: A script to request deployment of the graph from the SMO.
-   **tasks.py**: An Invoke script to build, package, and push all project components.
-   **README.md**: This file.


## Usage with Invoke

All build and deployment tasks are managed with Invoke.

You can see a list of all available tasks and their descriptions by running:
```bash
invoke --list
```

### The Easy Way: All-in-One Command

To build the images, push them to the registry, package the artifacts, and push the artifacts in one go, simply run:

```bash
invoke all
```

### Step-by-Step Instructions

If you prefer to run each step manually, follow the commands below.

#### 1. Build and Push Docker Images

These tasks build the necessary Docker images and push them to the configured container registry.

```bash
# Build all three Docker images
invoke build-images

# Push the images to the registry (this will automatically run build-images first)
invoke push-images
```

#### 2. Package Helm Artifacts

This command uses `hdarctl` to package the Helm charts into distributable artifacts.

```bash
invoke package-artifacts
```
This will create four `.tar.gz` artifacts in your project root (one for each application and one for the HDAG).

#### 3. Push Artifacts to HDAR

This command pushes the packaged artifacts to the Hyper-Distributed Application Registry (HDAR).

```bash
invoke push-artifacts
```

#### 4. Deploy the Graph

Once all artifacts are available in the registry, use the provided script to trigger the deployment:

```bash
./create-existing-artifact.sh
```
