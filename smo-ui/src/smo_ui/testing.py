from smo_core.helpers import KarmadaHelper


# noinspection PyMissingConstructor
class MockKarmadaHelper(KarmadaHelper):
    """Mock Karmada helper for testing"""

    def __init__(self, *args, **kwargs):
        pass

    def get_cluster_info(self):
        return {"cluster1": {"name": "cluster1", "status": "Ready"}}

    def get_replicas(self, name):
        return 1

    def get_cpu_limit(self, name):
        return 1.0

    def scale_deployment(self, name, replicas):
        pass
