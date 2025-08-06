from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .routes import register_routers


def create_app():
    """Create and configure the FastAPI application."""
    app = FastAPI(title="SMO-UI")

    # Mount static files
    app.mount("/static", StaticFiles(directory="fastapi1/static"), name="static")

    # Register routers
    register_routers(app)

    return app


app = create_app()
