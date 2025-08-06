from contextlib import asynccontextmanager

from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .providers import main_providers
from .routes import register_routers


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await app.state.dishka_container.close()


def create_app():
    """Create and configure the FastAPI application."""
    app = FastAPI(title="SMO-UI", lifespan=lifespan)

    # Mount static files
    app.mount("/static", StaticFiles(directory="src/smo_ui/static"), name="static")

    # Register routers and setup DI
    register_routers(app)
    container = make_async_container(*main_providers)
    setup_dishka(container=container, app=app)

    return app


app = create_app()
