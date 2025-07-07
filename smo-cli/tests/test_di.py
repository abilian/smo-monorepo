# from unittest.mock import MagicMock, patch
# import pytest
# from sqlalchemy import Engine
# from sqlalchemy.orm import Session
# from dishka import Provider, Scope, provide, make_container
#
# # Import the providers we want to test
# from smo_cli.providers import ConfigProvider, InfraProvider, DbProvider, Config
#
# # Import the real helpers to check types
# from smo_core.utils.karmada_helper import KarmadaHelper
# from smo_core.utils.prometheus_helper import PrometheusHelper
# from smo_core.utils.grafana_helper import GrafanaHelper
#
#
# # --- 1. Testing ConfigProvider ---
#
# def test_config_provider(mocker):
#     """
#     Tests that ConfigProvider correctly calls Config.load.
#     We mock Config.load to avoid actual file system access.
#     """
#     # Arrange: Create a mock config object to be returned by Config.load
#     mock_config_instance = Config()
#
#     # Mock the static method `Config.load` to return our mock instance
#     mocker.patch("smo_cli.providers.Config.load", return_value=mock_config_instance)
#
#     # Act: Create a container and get the Config
#     container = make_container(ConfigProvider())
#     resolved_config = container.get(Config)
#     container.close()
#
#     # Assert: Check that the resolved object is our mock and the method was called
#     assert resolved_config is mock_config_instance
#     from smo_cli.providers import Config as C
#     C.load.assert_called_once()
#
#
# # --- 2. Testing InfraProvider ---
#
# # Create mock helper classes for testing
# class MockKarmadaHelper:
#     def __init__(self, config_file_path: str, namespace: str = "default"):
#         pass
#
#
# class MockPrometheusHelper:
#     pass
#
#
# class MockGrafanaHelper:
#     pass
#
#
# class MockInfraProvider(Provider):
#     """
#     This is a test provider that overrides the real infrastructure providers
#     with our simple mock classes. `override=True` is crucial.
#     """
#     scope = Scope.APP
#
#     karmada = provide(MockKarmadaHelper, provides=KarmadaHelper, override=True)
#     prometheus = provide(MockPrometheusHelper, provides=PrometheusHelper, override=True)
#     grafana = provide(MockGrafanaHelper, provides=GrafanaHelper, override=True)
#
#
# def test_infra_provider_overrides():
#     """
#     Tests that InfraProvider can be successfully overridden with mocks.
#     This pattern is key for integration testing higher-level services.
#     """
#     # Arrange: Create a container with the real provider AND our mock provider.
#     # Dishka uses the last provider registered for a given type, effectively
#     # allowing MockInfraProvider to override InfraProvider.
#     container = make_container(InfraProvider(), MockInfraProvider())
#
#     # Act: Get each helper from the container
#     karmada = container.get(KarmadaHelper)
#     prometheus = container.get(PrometheusHelper)
#     grafana = container.get(GrafanaHelper)
#     container.close()
#
#     # Assert: Verify that the retrieved objects are instances of our mock classes
#     assert isinstance(karmada, MockKarmadaHelper)
#     assert isinstance(prometheus, MockPrometheusHelper)
#     assert isinstance(grafana, MockGrafanaHelper)
#
#
# # --- 3. Testing DbProvider ---
#
# @pytest.fixture
# def mock_config() -> Config:
#     """A pytest fixture to create a mock Config object for database tests."""
#     config = MagicMock(spec=Config)
#     # Configure the mock to use an in-memory SQLite database
#     config.db_file = ":memory:"
#     return config
#
#
# class TestConfigProvider(Provider):
#     """A test provider specifically to inject our mock_config."""
#
#     def __init__(self, config: Config):
#         super().__init__()
#         self._config = config
#
#     @provide(scope=Scope.APP, override=True)
#     def get_config(self) -> Config:
#         return self._config
#
#
# def test_db_provider_get_engine(mock_config):
#     """
#     Tests that get_engine provider creates a SQLAlchemy Engine correctly
#     based on the (mocked) config.
#     """
#     # Arrange: Create a container with DbProvider and our TestConfigProvider
#     container = make_container(DbProvider(), TestConfigProvider(config=mock_config))
#
#     # Act
#     engine = container.get(Engine)
#     container.close()
#
#     # Assert
#     assert isinstance(engine, Engine)
#     # Check that the URL was constructed correctly from our mock config
#     assert str(engine.url) == "sqlite:///:memory:"
#
#
# def test_db_provider_session_finalization(mock_config, mocker):
#     """
#     Tests that the generator-based session provider correctly finalizes
#     (i.e., calls `session.close()`).
#     """
#     # Arrange:
#     # We need to spy on the `session.close` method to see if it's called.
#     mock_session_instance = MagicMock(spec=Session)
#
#     # We patch the sessionmaker() call inside the provider to return a
#     # factory that creates our mock_session_instance.
#     mocker.patch(
#         "smo_cli.providers.sessionmaker",
#         return_value=lambda bind: lambda: mock_session_instance
#     )
#
#     # Act:
#     # We create and use the container within a context manager.
#     # Exiting the `with` block will trigger container.close(),
#     # which in turn should trigger the finalization of the session generator.
#     container = make_container(DbProvider(), TestConfigProvider(config=mock_config))
#     with container.get(Session) as session:
#         pass
#     #     # Get the session from the container
#     # session = container.get(Session)
#     container.close()
#
#     # Assert that we got our mock session and `close` has not been called yet.
#     assert session is mock_session_instance
#     mock_session_instance.close.assert_not_called()
#
#     # Assert: After exiting the `with` block, `close` must have been called.
#     mock_session_instance.close.assert_called_once()
