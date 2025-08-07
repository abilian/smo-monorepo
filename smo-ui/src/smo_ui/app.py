from contextlib import asynccontextmanager
from pathlib import Path

from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .providers import main_providers
from .routes import register_routers

PACKAGE_DIR = Path(__file__).parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await app.state.dishka_container.close()


def create_bare_app():
    """Create and configure a bare (no DI config) FastAPI application."""
    app = FastAPI(title="SMO-UI", lifespan=lifespan)
    app.mount("/static", StaticFiles(directory=PACKAGE_DIR / "static"), name="static")
    register_routers(app)
    return app


def create_app(container: AsyncContainer = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    app = create_bare_app()

    if container is None:
        container = make_async_container(*main_providers)

    setup_dishka(container=container, app=app)
    return app


app = create_app()
