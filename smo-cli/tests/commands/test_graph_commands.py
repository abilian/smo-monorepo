from click.testing import CliRunner
from tests.conftest import MockGraphService

from smo_cli.cli import main
from smo_cli.commands.exceptions import CliException


def test_graph_deploy_from_file(
    client: CliRunner, hdag_file: str, mock_graph_service: MockGraphService
):
    result = client.invoke(
        main, ["-v", "graph", "deploy", "--project", "test-proj", hdag_file]
    )
    assert result.exit_code == 0
    mock_graph_service.deploy_graph.assert_called_once()


def test_graph_deploy_invalid_file(client: CliRunner, tmp_path):
    invalid_file = tmp_path / "invalid.yaml"
    invalid_file.write_text("key: value")
    result = client.invoke(
        main, ["-v", "graph", "deploy", "--project", "p", str(invalid_file)]
    )
    assert result.exit_code != 0
    assert "Error: Invalid HDAG descriptor format" in result.output


def test_graph_list_no_project(client: CliRunner):
    """Tests `graph list` without the --project flag. Should use the mock db_session."""
    result = client.invoke(main, ["-v", "graph", "list"])
    assert result.exit_code == 0, result.output
    # This comes from the mock db_session defined on the MockGraphService
    assert "db-graph" in result.output


def test_graph_describe(client: CliRunner):
    """Tests the 'graph describe' command for a found graph."""
    result = client.invoke(main, ["-v", "graph", "describe", "my-graph"])
    assert result.exit_code == 0, result.output
    # Check for content from the mocked .to_dict() return value
    assert "Project: default" in result.output
    assert "Status: Running" in result.output


def test_graph_describe_not_found(client: CliRunner):
    """Tests 'graph describe' when the graph is not found."""
    result = client.invoke(main, ["-v", "graph", "describe", "non-existent-graph"])
    assert result.exit_code != 0
    assert isinstance(result.exception, CliException)
    assert "Graph 'non-existent-graph' not found" in str(result.exception)


def test_graph_start(client: CliRunner, mock_graph_service: MockGraphService):
    result = client.invoke(main, ["-v", "graph", "start", "my-graph"])
    assert result.exit_code == 0
    mock_graph_service.start_graph.assert_called_once_with("my-graph")


def test_graph_stop(client: CliRunner, mock_graph_service: MockGraphService):
    result = client.invoke(main, ["graph", "stop", "my-graph"], input="y\n")
    assert result.exit_code == 0
    mock_graph_service.stop_graph.assert_called_once_with("my-graph")
