from fastapi import FastAPI
from dishka.integrations.fastapi import DishkaRoute

from . import clusters, docs, events, graphs, main, marketplace, projects, settings


def register_routers(app: FastAPI):
    """Register all routers for the application."""
    # Use DishkaRoute for all routers to enable auto-injection
    app.include_router(main.router, route_class=DishkaRoute)
    app.include_router(projects.router, route_class=DishkaRoute)
    app.include_router(graphs.router, route_class=DishkaRoute)
    app.include_router(clusters.router, route_class=DishkaRoute)
    app.include_router(marketplace.router, route_class=DishkaRoute)
    app.include_router(events.router, route_class=DishkaRoute)
    app.include_router(settings.router, route_class=DishkaRoute)
    app.include_router(docs.router, route_class=DishkaRoute)
