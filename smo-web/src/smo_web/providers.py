from copy import deepcopy
from dataclasses import dataclass
from typing import AsyncIterator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from smo_core.helpers import GrafanaHelper, KarmadaHelper, PrometheusHelper
from smo_core.models.base import Base

from .config import config


@dataclass(frozen=True)
class Config:
    _config: dict

    def get(self, *keys: list[str]):
        value = deepcopy(self._config)
        for key in keys:
            value = value[key]

        return value


class ConfigProvider(Provider):
    @provide(scope=Scope.APP)
    def get_config(self) -> Config:
        return Config(config)


class InfraProvider(Provider):
    scope = Scope.APP

    @provide
    def get_karmada(self, config: Config) -> KarmadaHelper:
        return KarmadaHelper(config.get("karmada_kubeconfig"))

    @provide
    def get_prometheus(self, config: Config) -> PrometheusHelper:
        return PrometheusHelper(config.get("prometheus_host"))

    @provide
    def get_grafana(self, config: Config) -> GrafanaHelper:
        return GrafanaHelper(
            config.get("grafana", "host"),
            config.get("grafana", "username"),
            config.get("grafana", "password"),
        )


class DbProvider(Provider):
    scope = Scope.APP

    @provide
    async def get_engine(self, config: Config):
        """Creates the SQLAlchemy async engine once."""
        db_cfg = config.get("db")
        db_uri = f"postgresql+asyncpg://{db_cfg['user']}:{db_cfg['password']}@{db_cfg['host']}:{db_cfg['port']}/{db_cfg['name']}"

        engine = create_async_engine(db_uri)
        await self.init_db(engine)
        return engine

    async def init_db(self, engine):
        """Create tables if they don't exist."""
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @provide
    def get_session_factory(self, engine) -> async_sessionmaker[AsyncSession]:
        """Creates a session factory, which is cheap to create."""
        return async_sessionmaker(engine, expire_on_commit=False)

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self, factory: async_sessionmaker[AsyncSession]
    ) -> AsyncIterator[AsyncSession]:
        """Provides a request-scoped database session."""
        async with factory() as session:
            yield session


# Combine all providers
def get_providers():
    return [ConfigProvider(), InfraProvider(), DbProvider()]
