from click.testing import CliRunner

from smo_cli.cli import main


def test_graph_deploy_from_file(client: CliRunner, hdag_file: str, mock_graph_service):
    result = client.invoke(
        main, ["-v", "graph", "deploy", "--project", "test-proj", hdag_file]
    )
    assert result.exit_code == 0, result.output
    assert "Successfully triggered deployment" in result.output
    mock_graph_service.deploy_graph.assert_called_once()


def test_graph_deploy_from_oci(client: CliRunner, mocker, mock_graph_service):
    oci_url = "oci://my-registry/my-graph:1.0"
    mocker.patch(
        "smo_cli.commands.graph.get_graph_from_artifact",
        return_value={"hdaGraph": {"id": "oci-graph", "services": []}},
    )
    result = client.invoke(
        main, ["-v", "graph", "deploy", "--project", "oci-proj", oci_url]
    )
    assert result.exit_code == 0, result.output
    mock_graph_service.deploy_graph.assert_called_once()


def test_graph_list(client: CliRunner):
    result = client.invoke(main, ["-v", "graph", "list", "--project", "default"])
    assert result.exit_code == 0, result.output
    assert "default-graph-1" in result.output


def test_graph_remove(client: CliRunner, mock_graph_service):
    result = client.invoke(main, ["graph", "remove", "my-graph"], input="y\n")
    assert result.exit_code == 0, result.output
    mock_graph_service.remove_graph.assert_called_once_with("my-graph")


def test_graph_re_place(client: CliRunner, mock_graph_service):
    result = client.invoke(main, ["-v", "graph", "re-place", "my-graph"])
    assert result.exit_code == 0, result.output
    mock_graph_service.trigger_placement.assert_called_once_with("my-graph")
