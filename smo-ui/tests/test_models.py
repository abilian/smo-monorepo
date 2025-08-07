from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from smo_core.models import Cluster, Graph, Service
from smo_core.models.base import Base
from smo_ui.models.events import Event

TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_session():
    """
    Fixture to provide a test database session for model tests.
    It creates all tables for each test and rolls back transactions.
    """
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_event_model(db_session: Session):
    """Test Event model creation"""
    test_meta = {"key": "value"}
    event = Event(icon="🚀", message="Test event", source="test", meta=test_meta)
    db_session.add(event)
    db_session.commit()

    assert event.id is not None
    assert event.icon == "🚀"
    assert event.message == "Test event"
    assert event.source == "test"
    assert isinstance(event.timestamp, datetime)
    assert event.meta == test_meta

    event_dict = event.to_dict()
    assert event_dict["icon"] == "🚀"
    assert event_dict["message"] == "Test event"
    assert event_dict["source"] == "test"
    assert "timestamp" in event_dict
    assert event_dict["metadata"] == test_meta


def test_cluster_model(db_session: Session):
    """Test Cluster model creation"""
    cluster = Cluster(
        name="test-cluster",
        location="us-west",
        acceleration=True,
        available_cpu=4.0,
        available_ram="8GiB",
        availability=True,
    )
    db_session.add(cluster)
    db_session.commit()

    assert cluster.id is not None
    assert cluster.name == "test-cluster"
    assert cluster.to_dict()["name"] == "test-cluster"


def test_graph_model(db_session: Session):
    """Test Graph model creation"""
    graph = Graph(
        name="test-graph",
        project="default",
        status="Running",
        graph_descriptor={"id": "test-graph", "version": "1.0.0"},
    )
    db_session.add(graph)
    db_session.commit()

    assert graph.id is not None
    assert graph.name == "test-graph"
    assert graph.to_dict()["name"] == "test-graph"


def test_service_model(db_session: Session):
    """Test Service model creation"""
    service = Service(
        name="test-service", status="Running", cpu=1.0, memory="1GiB", graph_id=1
    )
    db_session.add(service)
    db_session.commit()

    assert service.id is not None
    assert service.name == "test-service"
    assert service.to_dict()["name"] == "test-service"
