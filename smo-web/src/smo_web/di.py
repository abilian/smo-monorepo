import inspect
from functools import wraps
from typing import Callable

import connexion
from dishka import AsyncContainer, FromDishka

DISHKA_CONTAINER_KEY = "dishka_container"


class DishkaMiddleware:
    def __init__(self, app, container: AsyncContainer):
        self._app = app
        self._container = container

    async def __call__(self, scope, receive, send):
        if scope["type"] not in ("http", "websocket"):
            await self._app(scope, receive, send)
            return

        async with self._container() as request_container:
            scope[DISHKA_CONTAINER_KEY] = request_container
            await self._app(scope, receive, send)


def inject(func: Callable) -> Callable:
    """Decorator to inject dependencies into a Connexion handler."""
    signature = inspect.signature(func)

    # Get the type hints of parameters marked for injection
    dependencies = {
        param.name: param.annotation
        for param in signature.parameters.values()
        if isinstance(param.annotation, FromDishka)
    }

    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Connexion places the request object in the `connexion.request` context-local
        request_container = connexion.request.scope.get(DISHKA_CONTAINER_KEY)

        if not request_container:
            raise RuntimeError(
                "Dishka container not found in request scope. Is the middleware configured?"
            )

        # Resolve dependencies
        for name, dep_type in dependencies.items():
            kwargs[name] = await request_container.get(dep_type.type)

        return await func(*args, **kwargs)

    return wrapper
