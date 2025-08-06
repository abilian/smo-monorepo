import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from smo_core.models import Cluster, Graph, Service
from smo_core.models.base import Base
from smo_ui.app import app
from smo_ui.extensions import get_db

assert Cluster and Graph and Service

# Setup test database
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables once at module level
Base.metadata.create_all(bind=engine)


# Not used yet.
class MockKarmadaHelper:
    """Mock Karmada helper for testing"""

    def get_cluster_info(self):
        return []

    def get_replicas(self, name):
        return 1

    def get_cpu_limit(self, name):
        return 1.0

    def scale_deployment(self, name, replicas):
        pass


@pytest.fixture
def db_session():
    """Fixture to provide a test database session"""
    # Create all tables fresh for each test
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture
def client(db_session):
    """Fixture to provide a test client with overridden dependencies"""

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def clean_db(db_session):
    """Clean database after each test"""
    yield
    # Clear all data but keep tables
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()
