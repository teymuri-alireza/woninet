from typing import List
from .models import MetricRecord

class StorageEngine:
    """
    Stores collected metric data.
    """
    def __init__(self):
        self.history: List[MetricRecord] = []

    def store(self, metrics: List[MetricRecord]):
        """
        Persist newly collected metrics.
        """
        self.history.extend(metrics)

    def get_history(self, ip: str, metric: str) -> List[MetricRecord]:
        """
        Retrieve historical metric records for a device.
        """
        return [m for m in self.history if m.device_ip == ip and m.metric == metric]
    
    def clear_history(self):
        """
        Clears history to prevent confusion in Alert section.
        """
        self.history = []