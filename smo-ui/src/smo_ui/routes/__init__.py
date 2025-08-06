from fastapi import FastAPI

from . import clusters, docs, events, graphs, main, marketplace, projects, settings


def register_routers(app: FastAPI):
    """Register all routers for the application."""
    app.include_router(main.router)
    app.include_router(projects.router)
    app.include_router(graphs.router)
    app.include_router(clusters.router)
    app.include_router(marketplace.router)
    app.include_router(events.router)
    app.include_router(settings.router)
    app.include_router(docs.router)
