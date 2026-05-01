import logging
from typing import List
from woninet.core.storage import StorageEngine

core_logger = logging.getLogger("core")


class AlertRule:
    """
    Defines a monitoring rule that triggers an alert
    when a metric exceeds a defined threshold.
    """

    def __init__(self, metric: str, threshold: float, duration: int) -> None:
        self.metric: str = metric
        self.threshold: float = threshold
        self.duration: int = duration


class AlertEngine:
    """
    Evaluates stored metrics against alert rules
    and generates alerts when conditions are violated.
    """

    def __init__(self, storage: StorageEngine, rules: List[AlertRule]) -> None:
        self.storage: StorageEngine = storage
        self.rules: List[AlertRule] = rules

    def evaluate(self) -> None:
        """
        Scan stored metrics and trigger alerts
        when thresholds are exceeded.
        """
        for rule in self.rules:
            for record in self.storage.get_metric_history():
                if record.value != 0:
                    if record.metric == rule.metric and record.value > rule.threshold:
                        core_logger.warning(
                            f"{record.device_ip} exceeded {rule.metric}: {record.value:.2f}"
                        )
        # Clear metric history to avoid repeated alerts
        self.storage.clear_metric_history()
