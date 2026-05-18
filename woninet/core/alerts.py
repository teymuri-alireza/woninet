import logging
from datetime import datetime
from woninet.core.storage import StorageEngine
from woninet.database.tables import AlertEventTable

core_logger = logging.getLogger("core")


class AlertRule:
    """
    Define a monitoring rule that triggers an alert
    when a metric exceeds a defined threshold.
    """

    def __init__(self, metric: str, threshold: float, consecutive_checks: int) -> None:
        """
        Initialize the alert rule.

        Args:
            metric: Name of the metric the rule evaluates.
            threshold: The Limit the metric must exceed to trigger the alert.
            consecutive_checks: Number of consecutive evaluations required before
                a state change.
        """
        self.metric: str = metric
        self.threshold: float = threshold
        self.consecutive_checks: int = consecutive_checks


class AlertEngine:
    """
    Evaluate stored metrics against alert rules
    and generates alerts when conditions are violated.
    """

    def __init__(self, storage: StorageEngine, rule: AlertRule) -> None:
        """
        Initialize the alert engine.

        Args:
            storage: Storage backend used to manage database sessions.
            rules: Alert rule evaluated against stored metrics.
        """
        self.storage: StorageEngine = storage
        self.rule: AlertRule = rule

    def is_metric_violated(self, metric: str, value: float) -> bool:
        """
        Check if a metric value violates a specific rule.
        """
        return metric == self.rule.metric and value > self.rule.threshold

    def evaluate(
        self, ip: str, metric: str, value: float, default_consecutive_checks: int
    ) -> None:
        """
        Update an alert state and create an alert event if a specific rule
        is violated and the status of a device is changed (e.g., from "ok"
        to "warning" or vice versa).
        """
        state = self.storage.get_or_create_alert_state(
            ip=ip, metric=metric, consecutive_checks=default_consecutive_checks
        )
        violated = self.is_metric_violated(metric=metric, value=value)
        if violated:
            if state.state == "ok":
                # Confirm remaining consecutive checks for before a state change
                if state.consecutive_checks > 0:
                    state.consecutive_checks = state.consecutive_checks - 1
                    self.storage.update_alert_state(state)
                    return
                # Update "ok" to "warning"
                state.state = "warning"
                state.triggered_at = datetime.now()
                state.consecutive_checks = default_consecutive_checks
                self.storage.update_alert_state(state)

                event = AlertEventTable(
                    device_ip=ip, metric=metric, value=value, event_type="trigger"
                )
                self.storage.store_alert_event(event=event)
                core_logger.warning(
                    f"ALERT TRIGGERED | {ip}, metric={metric}, value={value} ms"
                )
            else:
                # Reset consecutive checks to its default value
                state.consecutive_checks = default_consecutive_checks
                self.storage.update_alert_state(state)
        else:
            if state.state == "warning":
                # Confirm remaining consecutive checks for before a state change
                if state.consecutive_checks > 0:
                    state.consecutive_checks = state.consecutive_checks - 1
                    self.storage.update_alert_state(state)
                    return
                # Update "warning" to "ok"
                state.state = "ok"
                state.triggered_at = None
                state.consecutive_checks = default_consecutive_checks
                self.storage.update_alert_state(state)

                event = AlertEventTable(
                    device_ip=ip, metric=metric, value=value, event_type="recover"
                )
                self.storage.store_alert_event(event=event)
                core_logger.warning(
                    f"ALERT RECOVERED | {ip}, metric={metric}, value={value} ms"
                )
            else:
                # Reset consecutive checks to its default value
                state.consecutive_checks = default_consecutive_checks
                self.storage.update_alert_state(state)
