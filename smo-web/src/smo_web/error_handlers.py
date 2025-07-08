import connexion
from connexion.problem import problem
from starlette.exceptions import HTTPException


def handle_value_error(request, exc: ValueError):
    """Catches errors raised from smo-core services (e.g., graph not found)."""
    return problem(status=400, title="Bad Request", detail=str(exc))


def handle_not_found(request, exc: HTTPException):
    """Handles 404 errors for unregistered paths."""
    return problem(status=404, title="Not Found", detail=exc.detail)


def handle_generic_exception(request, exc: Exception):
    """A catch-all for unexpected errors."""
    # In a production app, you would log the full exception here
    print(f"Caught unhandled exception: {exc}")
    return problem(
        status=500,
        title="Internal Server Error",
        detail="An unexpected error occurred.",
    )


def register_error_handlers(app: connexion.AsyncApp):
    app.add_error_handler(404, handle_not_found)
    app.add_error_handler(ValueError, handle_value_error)
    app.add_error_handler(Exception, handle_generic_exception)
