from typing import List
from woninet.core.models import Device
from woninet.core.models import MetricRecord


class StorageEngine:
    """
    Stores collected device and metric data.
    """

    def __init__(self) -> None:
        self.history: List[Device] = []
        self.metric_history: List[MetricRecord] = []

    def store(self, device: Device) -> None:
        """
        Store newly collected devices.
        """
        # Update data if device is in history
        if device in self.history:
            for i in range(len(self.history)):
                if self.history[i].ip == device.ip:
                    self.history[i].latency = device.latency
                    self.history[i].last_seen = device.last_seen
                    break
        else:
            self.history.append(device)

    def get_history(self) -> List[Device]:
        """
        Returns history records for all devices.
        """
        return self.history

    def store_metric(self, metrics: List[MetricRecord]) -> None:
        """
        Persist newly collected metrics
        """

        self.metric_history.extend(metrics)

    def get_metric_history(self) -> List[MetricRecord]:
        """
        Returns history records for metric data.
        """
        return self.metric_history

    def clear_metric_history(self) -> None:
        """
        Clear stored metric history.
        """
        self.metric_history = []
