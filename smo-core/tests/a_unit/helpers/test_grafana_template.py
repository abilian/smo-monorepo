import pytest

from smo_core.helpers.grafana.grafana_template import (
    create_basic_dashboard,
    create_dashboard_variables,
    create_panels_cluster,
    create_panels_service,
)


def test_create_basic_dashboard():
    """Test creating a basic dashboard skeleton."""
    dashboard = create_basic_dashboard("test-dashboard")
    assert dashboard["dashboard"]["title"] == "test-dashboard"
    assert dashboard["dashboard"]["panels"] == []
    assert dashboard["overwrite"] is True


def test_create_dashboard_variables():
    """Test creating dashboard variables."""
    variables = create_dashboard_variables("test_var", ["val1", "val2"])
    assert len(variables["list"]) == 1
    var = variables["list"][0]
    assert var["name"] == "test_var"
    assert var["query"] == "val1, val2"
    assert len(var["options"]) == 2


def test_create_panels_service():
    """Test creating service panels."""
    panels = create_panels_service("test-service")
    assert len(panels) == 4
    assert all(p["title"].startswith("test-service") for p in panels)
    assert all(p["type"] == "timeseries" for p in panels)


def test_create_panels_cluster():
    """Test creating cluster panels."""
    panels = create_panels_cluster("test-cluster")
    assert len(panels) == 9
    panel_types = {p["type"] for p in panels}
    assert panel_types == {"timeseries", "stat", "gauge"}
