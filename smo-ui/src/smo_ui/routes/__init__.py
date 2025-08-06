from fastapi import FastAPI
from dishka.integrations.fastapi import setup_dishka
from dishka import make_container

from . import clusters, docs, events, graphs, main, marketplace, projects, settings
from ..providers import main_providers


def register_routers(app: FastAPI):
    """Register all routers for the application."""
    # Setup DI container
    container = make_container(*main_providers)
    setup_dishka(container, app)

    app.include_router(main.router)
    app.include_router(projects.router)
    app.include_router(graphs.router)
    app.include_router(clusters.router)
    app.include_router(marketplace.router)
    app.include_router(events.router)
    app.include_router(settings.router)
    app.include_router(docs.router)
