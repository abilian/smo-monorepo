from dataclasses import dataclass

from smo_core.helpers import KarmadaHelper, PrometheusHelper


@dataclass(frozen=True)
class ScalerService:
    """Placeholder for the ScalerService class."""

    karmada: KarmadaHelper
    prometheus: PrometheusHelper

    def run_threshold_scaler_iteration(
        self,
        target_deployment: str,
        target_namespace: str,
        scale_up_threshold: float,
        scale_down_threshold: float,
        scale_up_replicas: int,
        scale_down_replicas: int,
    ) -> dict:
        """
        Performs a single iteration of the threshold-based scaling logic.
        This function is stateless and relies on the caller to manage loops and cooldowns.

        Returns:
            A dictionary describing the action taken, e.g.,
            {'action': 'scale_up', 'new_replicas': 3, 'reason': 'RPS > threshold'}
        """
        return _run_threshold_scaler_iteration(
            self.karmada,
            self.prometheus,
            target_deployment,
            target_namespace,
            scale_up_threshold,
            scale_down_threshold,
            scale_up_replicas,
            scale_down_replicas,
        )


def _run_threshold_scaler_iteration(
    karmada: KarmadaHelper,
    prometheus: PrometheusHelper,
    target_deployment: str,
    target_namespace: str,
    scale_up_threshold: float,
    scale_down_threshold: float,
    scale_up_replicas: int,
    scale_down_replicas: int,
) -> dict:
    try:
        # Get current state from Kubernetes
        deployment = karmada.v1_api_client.read_namespaced_deployment(
            target_deployment, target_namespace
        )
        current_replicas = deployment.spec.replicas

        # Get metric from Prometheus
        request_rate = prometheus.get_request_rate_by_job(target_deployment)

        if request_rate is None:
            return {
                "action": "none",
                "reason": "Could not retrieve metrics from Prometheus.",
                "current_replicas": current_replicas,
            }

        # --- Scaling Decision Logic ---
        if request_rate > scale_up_threshold and current_replicas < scale_up_replicas:
            print(
                f"ACTION: Scaling UP. Rate {request_rate:.2f} > Threshold {scale_up_threshold:.2f}"
            )
            karmada.scale_deployment(target_deployment, scale_up_replicas)
            return {
                "action": "scale_up",
                "new_replicas": scale_up_replicas,
                "reason": f"Request rate {request_rate:.2f} RPS exceeded scale-up threshold of {scale_up_threshold:.2f} RPS.",
                "current_replicas": current_replicas,
            }
        elif (
            request_rate < scale_down_threshold
            and current_replicas > scale_down_replicas
        ):
            print(
                f"ACTION: Scaling DOWN. Rate {request_rate:.2f} < Threshold {scale_down_threshold:.2f}"
            )
            karmada.scale_deployment(target_deployment, scale_down_replicas)
            return {
                "action": "scale_down",
                "new_replicas": scale_down_replicas,
                "reason": f"Request rate {request_rate:.2f} RPS is below scale-down threshold of {scale_down_threshold:.2f} RPS.",
                "current_replicas": current_replicas,
            }
        else:
            return {
                "action": "none",
                "reason": "Request rate is within thresholds or deployment is already at target replicas.",
                "current_replicas": current_replicas,
                "request_rate": request_rate,
            }

    except Exception as e:
        print(f"Error during scaling iteration: {e}")
        return {"action": "error", "reason": str(e)}
