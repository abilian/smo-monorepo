from pathlib import Path

from click.testing import CliRunner

from smo_cli.cli import main


def test_graph_deploy_from_file(
    runner: CliRunner, tmp_smo_dir: Path, mock_graph_service, hdag_file, mocker
):
    """Tests 'smo-cli graph deploy' with a local file."""
    # Mock the deployment to return successfully
    mock_graph_service.deploy_graph.return_value = None
    
    result = runner.invoke(
        main, ["graph", "deploy", "--project", "test-proj", hdag_file]
    )
    assert result.exit_code == 0
    assert "triggered deployment" in result.output

    mock_graph_service.deploy_graph.assert_called_once()


def test_graph_deploy_from_oci(runner, tmp_smo_dir: Path, mocker, mock_graph_service):
    """Tests 'smo-cli graph deploy' with an OCI URL."""
    oci_url = "oci://my-registry/my-graph:1.0"

    # Mock the artifact fetching function
    mock_graph_service.get_graph_from_artifact.return_value = {
        "hdaGraph": {"id": "oci-graph"}
    }

    result = runner.invoke(main, ["graph", "deploy", "--project", "oci-proj", oci_url])

    assert result.exit_code == 0
    assert "Deploying graph from" in result.output
    assert "oci-graph" in result.output

    mock_graph_service.deploy_graph.assert_called_once()


def test_graph_list(runner, tmp_smo_dir: Path, mock_graph_service, mocker):
    """Tests 'smo-cli graph list'."""
    mock_graph_service.fetch_project_graphs.return_value = [
        {
            "name": "test-graph",
            "project": "test-proj",
            "status": "Running",
            "services": [],
        }
    ]

    result = runner.invoke(main, ["graph", "list", "--project", "test-proj"])
    assert result.exit_code == 0
    assert "test-graph" in result.output
    assert "test-proj" in result.output


def test_graph_remove(runner, tmp_smo_dir: Path, mock_graph_service):
    """Tests 'smo-cli graph remove' with user confirmation."""
    # Mock the graph to exist
    mock_graph_service.fetch_graph.return_value = {"name": "my-graph"}
    
    result = runner.invoke(
        main,
        ["graph", "remove", "my-graph"],
        input="y\n",
    )
    assert result.exit_code == 0
    assert "removed successfully" in result.output
    mock_graph_service.remove_graph.assert_called_once()


def test_graph_remove_abort(runner, tmp_smo_dir, mock_graph_service):
    """Tests 'smo-cli graph remove' with user aborting."""
    result = runner.invoke(
        main,
        ["graph", "remove", "my-graph"],
        input="n\n",  # Simulate user typing 'n'
    )

    assert result.exit_code == 1  # Abort raises an exit code
    assert "aborted" in result.output

    # Ensure the core service function was NOT called
    mock_graph_service.remove_graph.assert_not_called()


def test_graph_re_place(runner, tmp_smo_dir, mock_graph_service):
    """Tests 'smo-cli graph re-place'."""
    # Mock the graph to exist
    mock_graph_service.fetch_graph.return_value = {"name": "my-graph"}
    
    result = runner.invoke(main, ["graph", "re-place", "my-graph"])
    assert result.exit_code == 0 
    assert "Triggering re-placement" in result.output
    mock_graph_service.trigger_placement.assert_called_once()
