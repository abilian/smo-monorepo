from click.testing import CliRunner

from smo_cli.cli import main


def test_scaler_run(client: CliRunner, mocker):
    """
    Tests the 'smo-cli scaler run' command.
    We patch `time.sleep` to raise KeyboardInterrupt to break the infinite loop.
    """
    mocker.patch("time.sleep", side_effect=KeyboardInterrupt)

    result = client.invoke(
        main,
        [
            "scaler",
            "run",
            "--target-deployment",
            "test-deploy",
            "--up-threshold",
            "10",
            "--down-threshold",
            "2",
            "--up-replicas",
            "3",
            "--down-replicas",
            "1",
        ],
    )

    # FIX: A KeyboardInterrupt is an unhandled exception for the runner,
    # so it results in a non-zero exit code. This is expected.
    assert result.exit_code != 0

    # We can still check that the service was called before the interruption.
    assert "SCALING ACTION TAKEN" in result.output
    assert "Mocked scaling action" in result.output
