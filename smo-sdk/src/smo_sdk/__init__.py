"""A client library for accessing Synergetic Meta-Orchestrator (SMO) API"""

from .client import AuthenticatedClient, Client

__all__ = (
    "AuthenticatedClient",
    "Client",
)
