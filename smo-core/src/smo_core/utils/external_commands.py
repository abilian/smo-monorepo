import subprocess


def run_hdarctl(command: str, *args: str) -> str:
    """
    Run the `hdarctl` command with the specified arguments and return the output.

    :param command: The command to run (e.g., 'status', 'start', 'stop').
    :param args: Additional arguments for the command.
    :return: The output of the command as a string.
    """
    cmd = ["hdarctl", command] + list(args)
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def run_helm(command: str, *args: str) -> str:
    """
    Run the `helm` command with the specified arguments and return the output.

    :param command: The helm command to run (e.g., 'install', 'uninstall').
    :param args: Additional arguments for the command.
    :return: The output of the command as a string.
    """
    cmd = ["helm", command] + [str(arg) for arg in args if arg is not None]
    print(f"Running command: {' '.join(cmd)}")
    # result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)

    if result.returncode != 0:
        print(f"Command failed: {' '.join(cmd)}")
        print(f"Error: {result.stderr.strip()}")
        msg = f"Command '{' '.join(cmd)}' failed with return code {result.returncode}"
        raise subprocess.SubprocessError(msg)

    return result.stdout.strip()
