import os
from invoke import task, Context

# --- Configuration ---
# You can change these values or load them from environment variables/config files.
HOST_IP = os.environ.get("HOST_IP", "127.0.0.1")
REGISTRY = f"{HOST_IP}:5000"
HDAR_URL = f"http://{HOST_IP}:5000"
PROJECT = "test"


@task(default=True)
def help(c: Context):
    """Shows the help message, which is the default task."""
    print("Usage: invoke <task_name>\n")
    print("Invoke's built-in help is recommended. Try:")
    print("  invoke --list   (to see all available tasks)")
    print("  invoke --help <task_name> (to see help for a specific task)\n")
    c.run("invoke --list")


@task
def all(c: Context):
    """Alias for the 'help' task."""
    build_images(c)
    push_images(c)
    package_artifacts(c)
    push_artifacts(c)


@task
def build_images(c: Context):
    """Build all docker images."""
    print("Building docker images...")
    images = {
        "custom-vo": "src/virtual-object/",
        "noise-reduction": "src/noise-reduction/",
        "image-detection": "src/image-detection/",
    }
    for name, path in images.items():
        print(f"--> Building {name}")
        c.run(f'docker build -t "{REGISTRY}/{name}" {path}')
    print("All images built successfully.")


@task(pre=[build_images])
def push_images(c: Context):
    """Push all docker images to the registry (runs build-images first)."""
    print("Pushing images to the registry...")
    images = ["custom-vo", "noise-reduction", "image-detection"]
    for image in images:
        print(f"--> Pushing {image}")
        c.run(f'docker push "{REGISTRY}/{image}"')
    print("All images pushed successfully.")


@task
def registry_login(c: Context):
    """Login to the HDAR registry."""
    print(f"Logging in to HDAR located at {HDAR_URL}...")
    c.run(f"hdarctl login {HDAR_URL}")


@task
def change_ips(c: Context):
    """Changes the IPs declared in the artifacts to the proper ones."""
    print(f"Running IP fix script for registry: {REGISTRY}")
    c.run(f"./fix-ips.py {REGISTRY}")


@task
def package_artifacts(c: Context):
    """Package artifacts using hdarctl."""
    print("Packaging artifacts...")
    artifacts = [
        "image-detection/",
        "noise-reduction/",
        "image-compression-vo/",
        "hdag/",
    ]
    for artifact in artifacts:
        print(f"--> Packaging {artifact}")
        c.run(f"hdarctl package tar {artifact}")
    print("Artifacts packaged successfully.")


@task
def push_artifacts(c: Context):
    """Push packaged artifacts to the HDAR."""
    print(f"Pushing artifacts to {HDAR_URL}/{PROJECT}...")
    artifacts = [
        "image-detection-0.1.0.tar.gz",
        "noise-reduction-0.1.0.tar.gz",
        "image-compression-vo-0.1.0.tar.gz",
        "image-detection-graph-1.0.0.tar.gz",
    ]
    for artifact in artifacts:
        print(f"--> Pushing {artifact}")
        c.run(f"hdarctl push {artifact} {HDAR_URL}/{PROJECT}")
        print("")  # Newline for spacing
    print("Artifacts pushed successfully.")


@task
def deploy(c: Context):
    """Deploy the HDAR artifacts."""
    print("Deploying HDAR artifacts...")
    c.run(f"hdarctl deploy {HDAR_URL}/{PROJECT}/image-detection-graph-1.0.0.tar.gz")
    print("Deployment completed successfully.")


@task
def undeploy(c: Context):
    """Undeploy the HDAR artifacts."""
    print("Undeploying HDAR artifacts...")
    c.run(f"hdarctl undeploy {HDAR_URL}/{PROJECT}/image-detection-graph-1.0.0.tar.gz")
    print("Undeployment completed successfully.")
