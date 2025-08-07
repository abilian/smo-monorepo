import connexion
from connexion.options import SwaggerUIOptions

from .error_handlers import register_error_handlers

swagger_ui_options = SwaggerUIOptions(
    swagger_ui=True,
    swagger_ui_path="/docs",
)


def create_app(config_name: str = "") -> connexion.AsyncApp:
    app = connexion.AsyncApp(
        __name__,
        specification_dir="swagger",
        swagger_ui_options=swagger_ui_options,
    )

    app.add_api(
        "openapi.yaml",
        strict_validation=True,
        validate_responses=True,
    )

    register_error_handlers(app)

    return app
