from typing import List
from woninet.core.storage import StorageEngine
from woninet.utilities.logger import logger_function

rootLogger = logger_function()

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
            for record in self.storage.history:
                if record.value is not None and record.value is not False:
                    if record.metric == rule.metric and record.value > rule.threshold:
                        rootLogger.warning(f"[ALERT] {record.device_ip} exceeded {rule.metric}: {record.value:.2f}")
