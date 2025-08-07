from pathlib import Path

from click.testing import CliRunner

from smo_cli.cli import main


def test_graph_deploy_from_file(
    runner: CliRunner, tmp_smo_dir: Path, mock_graph_service, hdag_file, mocker
):
    """Tests 'smo-cli graph deploy' with a local file."""
    # Mock the graph to exist after deployment
    mock_graph = {"name": "test-graph", "project": "test-proj"}
    mock_graph_service.deploy_graph.return_value = mock_graph
    
    result = runner.invoke(
        main, ["graph", "deploy", "--project", "test-proj", hdag_file]
    )
    assert result.exit_code == 0
    assert "Successfully triggered deployment" in result.output
    assert "test-graph" in result.output

    mock_graph_service.deploy_graph.assert_called_once()


def test_graph_deploy_from_oci(runner, tmp_smo_dir: Path, mocker, mock_graph_service):
    """Tests 'smo-cli graph deploy' with an OCI URL."""
    oci_url = "oci://my-registry/my-graph:1.0"

    # Mock the graph to exist after deployment
    mock_graph = {"name": "oci-graph", "project": "oci-proj"}
    mock_graph_service.deploy_graph.return_value = mock_graph

    # Mock the artifact fetching
    mocker.patch(
        "smo_cli.commands.graph.get_graph_from_artifact",
        return_value={"hdaGraph": {"id": "oci-graph"}}
    )

    result = runner.invoke(main, ["graph", "deploy", "--project", "oci-proj", oci_url])
    assert result.exit_code == 0
    assert "Successfully triggered deployment" in result.output
    assert "oci-graph" in result.output

    mock_graph_service.deploy_graph.assert_called_once()


def test_graph_list(runner, tmp_smo_dir: Path, mock_graph_service, mocker):
    """Tests 'smo-cli graph list'."""
    # Mock the graph service to return a list of graphs
    mock_graph = {
        "name": "test-graph",
        "project": "test-proj",
        "status": "Running",
        "services": []
    }
    mock_graph_service.fetch_project_graphs.return_value = [mock_graph]

    result = runner.invoke(main, ["graph", "list", "--project", "test-proj"])
    assert result.exit_code == 0
    assert "test-graph" in result.output
    assert "test-proj" in result.output
    assert "Running" in result.output


def test_graph_remove(runner, tmp_smo_dir: Path, mock_graph_service):
    """Tests 'smo-cli graph remove' with user confirmation."""
    # Mock the graph to exist
    mock_graph = {"name": "my-graph", "project": "test-proj"}
    mock_graph_service.fetch_graph.return_value = mock_graph
    
    result = runner.invoke(
        main,
        ["graph", "remove", "my-graph"],
        input="y\n",
    )
    assert result.exit_code == 0
    assert "removed successfully" in result.output
    assert "my-graph" in result.output
    mock_graph_service.remove_graph.assert_called_once()


def test_graph_remove_abort(runner, tmp_smo_dir, mock_graph_service):
    """Tests 'smo-cli graph remove' with user aborting."""
    # Mock the graph to exist
    mock_graph = {"name": "my-graph", "project": "test-proj"}
    mock_graph_service.fetch_graph.return_value = mock_graph
    
    result = runner.invoke(
        main,
        ["graph", "remove", "my-graph"],
        input="n\n",  # Simulate user typing 'n'
    )

    assert result.exit_code == 1  # Abort raises an exit code
    assert "Aborted" in result.output
    assert "my-graph" in result.output

    # Ensure the core service function was NOT called
    mock_graph_service.remove_graph.assert_not_called()


def test_graph_re_place(runner, tmp_smo_dir, mock_graph_service):
    """Tests 'smo-cli graph re-place'."""
    # Mock the graph to exist
    mock_graph = {"name": "my-graph", "project": "test-proj"}
    mock_graph_service.fetch_graph.return_value = mock_graph
    
    result = runner.invoke(main, ["graph", "re-place", "my-graph"])
    assert result.exit_code == 0 
    assert "Triggering re-placement" in result.output
    assert "my-graph" in result.output
    mock_graph_service.trigger_placement.assert_called_once()
