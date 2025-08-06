from dishka import Provider, Scope, provide
from smo_core.context import SmoCoreContext
from smo_core.helpers import GrafanaHelper, KarmadaHelper, PrometheusHelper
from smo_ui.config import config_data


class ConfigProvider(Provider):
    """Provides configuration from config.yaml"""
    
    scope = Scope.APP

    @provide
    def get_config(self) -> dict:
        return config_data


class InfraProvider(Provider):
    """Provides infrastructure helpers"""
    
    scope = Scope.APP

    @provide
    def get_karmada(self, config: dict) -> KarmadaHelper:
        return KarmadaHelper(config["karmada"]["kubeconfig"])

    @provide
    def get_prometheus(self, config: dict) -> PrometheusHelper:
        return PrometheusHelper(config["prometheus"]["host"])

    @provide
    def get_grafana(self, config: dict) -> GrafanaHelper:
        grafana = config["grafana"]
        return GrafanaHelper(
            grafana["grafana_host"],
            grafana["username"],
            grafana["password"],
        )


class ContextProvider(Provider):
    """Provides SmoCoreContext"""
    
    scope = Scope.APP

    @provide
    def get_context(
        self,
        config: dict,
        karmada: KarmadaHelper,
        prometheus: PrometheusHelper,
        grafana: GrafanaHelper,
    ) -> SmoCoreContext:
        return SmoCoreContext(
            config=config,
            karmada=karmada,
            prometheus=prometheus,
            grafana=grafana,
        )


main_providers = [
    ConfigProvider(),
    InfraProvider(),
    ContextProvider(),
]
