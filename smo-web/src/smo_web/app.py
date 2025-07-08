import os
import connexion
from connexion.options import SwaggerUIOptions

# from .config import configs
# from .database import db
from .error_handlers import register_error_handlers


swagger_ui_options = SwaggerUIOptions(
    swagger_ui=True,
    swagger_ui_path="/docs",
)


def create_app(config_name: str = "") -> connexion.AsyncApp:
    if not config_name:
        config_name = os.environ.get("FLASK_ENV", "default")

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

    # app = connexion_app.app
    # app.config.from_object(configs[config_name])
    #
    # db.init_app(app)
    register_error_handlers(app)

    # with app.app_context():
    #     # This ensures all tables from smo_core are created
    #     from smo_core import models
    #
    #     db.create_all()

    return app
