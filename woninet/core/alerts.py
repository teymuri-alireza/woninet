import logging
from typing import List
from woninet.core.storage import StorageEngine

core_logger = logging.getLogger("core")


class AlertRule:
    """
    Define a monitoring rule that triggers an alert
    when a metric exceeds a defined threshold.
    """

    def __init__(self, metric: str, threshold: float, duration: int) -> None:
        """
        Initialize the alert rule.

        Args:
            metric: Name of the metric the rule evaluates.
            threshold: The Limit the metric must exceed to trigger the alert.
            duration: Number of consecutive checks the metric must exceed the threshold before triggering
        """
        self.metric: str = metric
        self.threshold: float = threshold
        self.duration: int = duration


class AlertEngine:
    """
    Evaluate stored metrics against alert rules
    and generates alerts when conditions are violated.
    """

    def __init__(self, storage: StorageEngine, rules: List[AlertRule]) -> None:
        """
        Initialize the alert engine.

        Args:
            storage: Storage backend used to manage database sessions.
            rules: Alert rules evaluated against stored metrics.
        """
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
