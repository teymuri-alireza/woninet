import logging
from datetime import datetime
from woninet.core.storage import StorageEngine
from woninet.core.models import MetricRecord
from woninet.database.tables import AlertEventTable

core_logger = logging.getLogger("core")


class AlertRule:
    """
    Define a monitoring rule that triggers an alert
    when a metric exceeds a defined threshold.

    Attributes:
        metric (str): Metric name to be evaluated.
        threshold (float): The Limit the metric must exceed to trigger the alert
        consecutive_checks (int): Number of consecutive evaluations required before
            a state change.
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

    Attributes:
        storage (StorageEngine): Backend interface for alert state persistence.
        rules (list[AlertRule]): Configuration describing metric threshold and evaluation logic.
    """

    def __init__(self, storage: StorageEngine, rules: list[AlertRule]) -> None:
        """
        Initialize the alert engine.

        Args:
            storage (StorageEngine): Storage backend used to manage database sessions.
            rules (list[AlertRule]): Alert rules evaluated against stored metrics.
        """
        self.storage: StorageEngine = storage
        self.rules: list[AlertRule] = rules

    def is_metric_violated(self, metric: str, value: float) -> bool:
        """
        Return True if the given metric exceeds the configured threshold.
        """
        for rule in self.rules:
            if metric == rule.metric:
                return value > rule.threshold
        # Fallback - No metric matched the configured rule.
        return False

    def evaluate(
        self,
        ip: str,
        metrics_list: list[MetricRecord],
        default_consecutive_checks: dict[str, int],
    ) -> None:
        """
        The central dispatcher.

        Search the metrics list for known metric's names (`latency_ms`, and `packet_loss`)
        and pass the found metric to the correct evaluation method.

        Args:
            ip (str): IP address to evaluate.
            metrics_name (list[MetricRecord]): List of recorded metrics (e.g. `latency_ms`, `packet_loss`).
            default_consecutive_checks (dict[str,int]): Dictionary of consecutive evaluations
                required to confirm a state transition for each metric.
        """
        for metric in metrics_list:
            if metric is not None:
                if metric.metric == "latency_ms":
                    self._evaluate_latency(
                        ip=ip,
                        metric="latency_ms",
                        value=metric.value,
                        default_consecutive_checks=default_consecutive_checks[
                            "latency_ms"
                        ],
                    )
                elif metric.metric == "packet_loss":
                    self._evaluate_packet_loss(
                        ip=ip,
                        metric="packet_loss",
                        value=metric.value,
                        default_consecutive_checks=default_consecutive_checks[
                            "packet_loss"
                        ],
                    )

    def _evaluate_latency(
        self, ip: str, metric: str, value: float, default_consecutive_checks: int
    ):
        """
        Evaluate a latency metric against the related alert rule.

        If the metric crosses its threshold for a consecutive number of checks,
        trigger or resolve an alert accordingly. Persists state transitions
        and logs any alert changes.

        Args:
            ip (str): IP address to evaluate.
            metric (str): Metric name (e.g. `latency_ms`).
            value (float): Value of the current metric.
            default_consecutive_checks (int): Number of consecutive evaluations
                required to confirm a state transition.

        Side Effects:
            - Persists alert state in the database via `StorageEngine`.
            - Emits log events.
            - Creates `AlertEventTable` records on trigger and recover.
        """
        state = self.storage.get_or_create_alert_state(
            ip=ip, metric=metric, consecutive_checks=default_consecutive_checks
        )
        violated = self.is_metric_violated(metric=metric, value=value)
        if violated:
            if state.state == "ok":
                # Confirm remaining consecutive checks before a state transition
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
                # Confirm remaining consecutive checks before a state transition
                if state.consecutive_checks > 0:
                    state.consecutive_checks = state.consecutive_checks - 1
                    self.storage.update_alert_state(state)
                    return
                # Update "warning" to "ok"
                state.state = "ok"
                state.triggered_at = datetime.now()
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

    def _evaluate_packet_loss(
        self, ip: str, metric: str, value: float, default_consecutive_checks: int
    ):
        """
        Evaluate a packet loss metric against the related alert rule.

        If the metric crosses its threshold for a consecutive number of checks,
        trigger or resolve an alert accordingly. Persists state transitions
        and logs any alert changes.

        Args:
            ip (str): IP address to evaluate.
            metric (str): Metric name (e.g. `packet_loss`).
            value (float): Value of the current metric.
            default_consecutive_checks (int): Number of consecutive evaluations
                required to confirm a state transition.

        **Side Effects**:
            - Persists alert state in the database via `StorageEngine`.
            - Emits log events.
            - Creates `AlertEventTable` records on trigger and recover.
        """
        state = self.storage.get_or_create_alert_state(
            ip=ip, metric=metric, consecutive_checks=default_consecutive_checks
        )
        violated = self.is_metric_violated(metric=metric, value=value)
        if violated:
            if state.state == "ok":
                # Confirm remaining consecutive checks before a state transition
                if state.consecutive_checks > 0:
                    state.consecutive_checks = state.consecutive_checks - 1
                    self.storage.update_alert_state(state)
                    return
                # Update "ok" to "warning"
                state.state = "warning"
                state.triggered_at = datetime.now()
                self.storage.update_alert_state(state)
                event = AlertEventTable(
                    device_ip=ip, metric=metric, value=value, event_type="trigger"
                )
                self.storage.store_alert_event(event=event)
                core_logger.warning(
                    f"ALERT TRIGGERED | {ip}, metric={metric}, value={value} %"
                )
            else:
                # Reset consecutive checks to its default value
                state.consecutive_checks = default_consecutive_checks
                self.storage.update_alert_state(state)
        else:
            if state.state == "warning":
                # Confirm remaining consecutive checks before a state transition
                if state.consecutive_checks > 0:
                    state.consecutive_checks = state.consecutive_checks - 1
                    self.storage.update_alert_state(state)
                    return
                # Update "warning" to "ok"
                state.state = "ok"
                state.triggered_at = datetime.now()
                self.storage.update_alert_state(state)
                event = AlertEventTable(
                    device_ip=ip, metric=metric, value=value, event_type="recover"
                )
                self.storage.store_alert_event(event=event)
                core_logger.warning(
                    f"ALERT RECOVERED | {ip}, metric={metric}, value={value} %"
                )
            else:
                # Reset consecutive checks to its default value
                state.consecutive_checks = default_consecutive_checks
                self.storage.update_alert_state(state)
