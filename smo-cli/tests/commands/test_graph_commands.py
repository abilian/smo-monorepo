from pathlib import Path

from click.testing import CliRunner

from smo_cli.cli import main


def test_graph_deploy_from_file(
    runner: CliRunner, tmp_smo_dir: Path, mock_graph_service, hdag_file
):
    """Tests 'smo-cli graph deploy' with a local file."""

    result = runner.invoke(
        main, ["graph", "deploy", "--project", "test-proj", hdag_file]
    )
    assert result.exit_code == 0
    assert "Successfully triggered deployment" in result.output

    # Assert that the core service was called with the correct arguments
    mock_graph_service.deploy_graph.assert_called_once()
    # Check the args passed to the mocked function
    args, kwargs = mock_graph_service.deploy_graph.call_args
    # args[0] is the context object, args[1] is the db session
    assert args[2] == "test-proj"  # project
    assert args[3]["id"] == "my-test-graph"  # graph_descriptor


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

    mock_graph_service.get_graph_from_artifact.assert_called_once_with(        oci_url
    )
    mock_graph_service.deploy_graph.assert_called_once()


def test_graph_list(runner, tmp_smo_dir: Path, mock_graph_service, mocker):
    """Tests 'smo-cli graph list'."""
    mock_graph_service.fetch_project_graphs.return_value = [
        {
            "name": "graph-1",
            "project": "proj-a",
            "status": "Running",
            "services": [{}, {}],
        },
        {"name": "graph-2", "project": "proj-a", "status": "Stopped", "services": [{}]},
    ]

    result = runner.invoke(main, ["graph", "list", "--project", "proj-a"])

    assert result.exit_code == 0
    assert "graph-1" in result.output
    assert "graph-2" in result.output
    assert "Running" in result.output
    assert "Stopped" in result.output

    mock_graph_service.fetch_project_graphs.assert_called_once_with(
        mocker.ANY, "proj-a"
    )


def test_graph_remove(runner, tmp_smo_dir: Path, mock_graph_service):
    """Tests 'smo-cli graph remove' with user confirmation."""
    result = runner.invoke(
        main,
        ["graph", "remove", "my-graph"],
        input="y\n",  # Simulate user typing 'y' and pressing Enter
    )

    assert result.exit_code == 0
    assert "Are you sure" in result.output
    assert "removed successfully" in result.output

    mock_graph_service.remove_graph.assert_called_once()
    # Check args
    args, _ = mock_graph_service.remove_graph.call_args
    assert args[2] == "my-graph"


def test_graph_remove_abort(runner, tmp_smo_dir, mock_graph_service):
    """Tests 'smo-cli graph remove' with user aborting."""
    result = runner.invoke(
        main,
        ["graph", "remove", "my-graph"],
        input="n\n",  # Simulate user typing 'n'
    )

    assert result.exit_code == 1  # Abort raises an exit code
    assert "Aborted!" in result.output

    # Ensure the core service function was NOT called
    mock_graph_service.remove_graph.assert_not_called()


def test_graph_re_place(runner, tmp_smo_dir, mock_graph_service):
    """Tests 'smo-cli graph re-place'."""
    result = runner.invoke(main, ["graph", "re-place", "my-graph"])

    assert result.exit_code == 0
    assert "Triggering re-placement" in result.output
    assert "completed successfully" in result.output

    mock_graph_service.trigger_placement.assert_called_once()
    args, _ = mock_graph_service.trigger_placement.call_args
    assert args[2] == "my-graph"
