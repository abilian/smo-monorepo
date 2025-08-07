# smo-cli/tests/commands/test_config_command.py

from click.testing import CliRunner

from smo_cli.cli import main


def test_config_command(client: CliRunner):
    """Tests the 'smo-cli config' command."""
    result = client.invoke(main, ["config"])
    assert result.exit_code == 0
    assert "Current configuration:" in result.output
    # Check for a key that should exist in the default config
    assert "karmada_kubeconfig" in result.output
