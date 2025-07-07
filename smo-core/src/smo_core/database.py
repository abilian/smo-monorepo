"""
Defines the SQLAlchemy declarative base.

Consumer applications (like smo-web or smo-cli) are responsible for creating
the database engine and session factory, and then calling:
`Base.metadata.create_all(engine)`
"""

from sqlalchemy.orm import declarative_base

# The single source of truth for all model definitions.
Base = declarative_base()
