import math

import requests
from kubernetes import client, config
from kubernetes.client.rest import ApiException


#
#  PUBLIC FACADE CLASS (Interface remains unchanged for callers)
#
class PrometheusHelper:
    """
    Helper class to query metrics and manage alerting rules in Prometheus.
    This class acts as a facade, delegating tasks to specialized clients.
    """

    def __init__(
        self, prometheus_host: str, time_window: str = "5", time_unit: str = "s"
    ):
        self.time_window = time_window
        self.time_unit = time_unit

        # Instantiate internal helpers, providing them with necessary configuration
        self._query_client = _PrometheusQueryClient(prometheus_host)
        self._rule_manager = _PrometheusRuleManager(
            reload_url=f"{prometheus_host}/-/reload"
        )

    def get_request_rate_by_job(self, job_name: str) -> float:
        """
        Queries Prometheus for the request rate of a target service,
        identified by its 'job' label.
        """
        # This query is taken directly from the h3ni-scaler logic
        query = f'sum(rate(http_requests_total{{job="{job_name}"}}[1m]))'
        rate = self._query_client.execute(query)

        if math.isnan(rate):
            print(f"No data received from Prometheus for job '{job_name}'.")
            # return 0.0  # Return 0 if no data, to allow for scale-down

        print(f"Current request rate for job '{job_name}': {rate:.2f} RPS")
        return rate

    def get_request_rate(self, name: str) -> float:
        """Returns the request completion rate of the service."""
        query = (
            f'sum(rate(flask_http_request_total{{service="{name}"}}'
            f"[{self.time_window}{self.time_unit}])) by (service)"
        )

        request_rate = self._query_client.execute(query)
        # The original behavior was to return 0.0 on failure or NaN, we preserve that.
        return 0.0 if math.isnan(request_rate) else request_rate

    def update_alert_rules(self, alert: dict, action: str) -> None:
        """
        Update prometheus rules depending on action. Either `add` or `remove`.
        Delegates the action to the internal rule manager.
        """
        # Hardcoded values from original implementation
        rule_file_name = "kube-prometheus-stack-0"
        namespace = "monitoring"
        group_name = "smo-alerts"

        if action.lower() == "add":
            self._rule_manager.add_alert(alert, rule_file_name, namespace, group_name)
        elif action.lower() == "remove":
            self._rule_manager.remove_alert(
                alert, rule_file_name, namespace, group_name
            )
        else:
            raise ValueError(
                f"Invalid action '{action}' for update_alert_rules. Must be 'add' or 'remove'."
            )


#
#  INTERNAL HELPER CLASSES (New Refactored Components)
#
class _PrometheusQueryClient:
    """Internal client focused solely on querying metrics from Prometheus."""

    def __init__(self, prometheus_host: str):
        if not prometheus_host:
            raise ValueError("Prometheus host URL cannot be empty.")
        self.api_endpoint = f"{prometheus_host.rstrip('/')}/api/v1/query"

    def execute(self, query: str) -> float:
        """
        Executes a PromQL query and returns the float value of the first result.
        Returns float('NaN') if no data is found or an error occurs.
        """
        try:
            response = requests.get(
                self.api_endpoint, params={"query": query}, timeout=5
            )
            response.raise_for_status()  # Raise an exception for bad status codes
            results = response.json()["data"]["result"]
            if results:
                return float(results[0]["value"][1])
        except requests.exceptions.RequestException as e:
            print(f"Warning: Prometheus request failed for query '{query}': {e}")
        except (KeyError, IndexError, ValueError) as e:
            print(
                f"Warning: Could not parse Prometheus response for query '{query}': {e}"
            )

        return float("NaN")


class _PrometheusRuleManager:
    """Internal manager for manipulating PrometheusRule CRDs in Kubernetes."""

    def __init__(self, reload_url: str):
        self.reload_url = reload_url
        self.api_instance = self._initialize_k8s_client()

    def _initialize_k8s_client(self):
        """Loads Kubernetes config and returns a CustomObjectsApi client."""
        try:
            config.load_kube_config()
            return client.CustomObjectsApi()
        except config.ConfigException as e:
            print(
                f"Warning: Could not load Kubernetes config: {e}. Rule management is disabled."
            )
            return None

    def add_alert(
        self, alert: dict, rule_file_name: str, namespace: str, group_name: str
    ):
        """Adds an alert rule to a specified group in a PrometheusRule file."""
        self._update_rules(alert, "add", rule_file_name, namespace, group_name)

    def remove_alert(
        self, alert: dict, rule_file_name: str, namespace: str, group_name: str
    ):
        """Removes an alert rule from a specified group."""
        self._update_rules(alert, "remove", rule_file_name, namespace, group_name)

    def _update_rules(
        self, alert: dict, action: str, crd_name: str, namespace: str, group_name: str
    ):
        """Core logic to fetch, modify, and update the PrometheusRule CRD."""
        if not self.api_instance:
            print("Cannot update alert rules: Kubernetes client not available.")
            return

        try:
            crd = self.api_instance.get_namespaced_custom_object(
                group="monitoring.coreos.com",
                version="v1",
                namespace=namespace,
                plural="prometheusrules",
                name=crd_name,
            )

            # Find the target group and modify its rules
            group_found = False
            for group in crd.get("spec", {}).get("groups", []):
                if group.get("name") == group_name:
                    group_found = True
                    rules = group.setdefault("rules", [])
                    if action == "add":
                        if not any(r.get("alert") == alert["alert"] for r in rules):
                            rules.append(alert)
                    elif action == "remove":
                        group["rules"] = [
                            r for r in rules if r.get("alert") != alert.get("alert")
                        ]
                    break

            if not group_found:
                print(
                    f"Error: Alert group '{group_name}' not found in PrometheusRule '{crd_name}'."
                )
                return

            # Push the updated CRD back to the cluster
            self.api_instance.replace_namespaced_custom_object(
                group="monitoring.coreos.com",
                version="v1",
                namespace=namespace,
                plural="prometheusrules",
                name=crd_name,
                body=crd,
            )
            print("PrometheusRule updated successfully.")
            self._trigger_prometheus_reload()

        except ApiException as e:
            print(f"Exception when updating PrometheusRule: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during rule update: {e}")

    def _trigger_prometheus_reload(self):
        """Sends a POST request to the Prometheus reload endpoint."""
        try:
            response = requests.post(self.reload_url, timeout=10)
            response.raise_for_status()
            print("Prometheus reloaded successfully.")
        except requests.exceptions.RequestException as e:
            print(f"Failed to reload Prometheus: {e}")
