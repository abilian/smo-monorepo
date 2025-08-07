from fastapi.templating import Jinja2Templates
from sqlalchemy.engine.create import create_engine
from sqlalchemy.orm.session import sessionmaker

from smo_core.context import SmoCoreContext
from smo_core.helpers import GrafanaHelper, PrometheusHelper
from smo_core.models.base import Base

from .config import config_data
from .testing import MockKarmadaHelper

templates = Jinja2Templates(directory="src/smo_ui/templates")


# --- Database Setup ---
DATABASE_URL = config_data["database"]["url"]
# `connect_args` is specific to SQLite for handling threads
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)
