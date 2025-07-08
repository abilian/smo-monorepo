"""
Defines the context object that will be passed to service functions.

This standardizes the way configuration and helper instances are accessed,
making the service layer independent of the calling application (web vs. cli).
"""

from dataclasses import dataclass

from .helpers import GrafanaHelper, KarmadaHelper, PrometheusHelper


@dataclass
class SmoContext:
    """A context object to hold application state."""

    config: dict
    karmada: KarmadaHelper
    prometheus: PrometheusHelper
    grafana: GrafanaHelper
