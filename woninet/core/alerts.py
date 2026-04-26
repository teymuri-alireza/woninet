from typing import List
from woninet.core.storage import StorageEngine
from woninet.utilities.logger import get_core_logger

core_logger = get_core_logger()


class AlertRule:
    """
    Defines a monitoring rule that triggers an alert
    when a metric exceeds a defined threshold.
    """

    def __init__(self, metric: str, threshold: float, duration: int):
        self.metric = metric
        self.threshold = threshold
        self.duration = duration


class AlertEngine:
    """
    Evaluates stored metrics against alert rules
    and generates alerts when conditions are violated.
    """

    def __init__(self, storage: StorageEngine, rules: List[AlertRule]):
        self.storage = storage
        self.rules = rules

    def evaluate(self):
        """
        Scan stored metrics and trigger alerts
        when thresholds are exceeded.
        """
        for rule in self.rules:
            for record in self.storage.get_metric_history():
                if record.value != 0:
                    if record.metric == rule.metric and record.value > rule.threshold:
                        core_logger.warning(
                            f"[ALERT] {record.device_ip} exceeded {rule.metric}: {record.value:.2f}"
                        )
        # Clear metric history to avoid repeated alerts
        self.storage.clear_metric_history()
