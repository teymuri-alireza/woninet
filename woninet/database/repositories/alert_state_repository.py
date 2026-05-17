from sqlalchemy.orm import Session
from woninet.database.tables import AlertStateTable


class AlertStateRepository:
    """
    Repository for presisting and updating Alert State entries.

    Encapsulate ORM operations on `AlertStateTable`.
    """

    def __init__(self, session: Session) -> None:
        """
        Initialize the repository.

        Args:
            session (Session): SQLAlchemy session used for all database operations.
        """
        self.session = session

    def fetch_or_create_alert_state(
        self, ip: str, metric: str, consecutive_checks: int
    ) -> AlertStateTable:
        """
        Return an alert state for a specfic IP address and metric; Create a new one
        if it already doesn't exist.

        Args:
            ip (str): IP address of host.
            metric (str): Name of the metric beaing monitored.
            consecutive_checks (int): Number of consecutive evaluations required
                before a state change.

        Returns:
            AlertStateTable: The found alert state for a given IP and metric,
                or a new alert state for new entries.
        """
        state = (
            self.session.query(AlertStateTable)
            .filter_by(device_ip=ip, metric=metric)
            .one_or_none()
        )

        if state is None:
            state = AlertStateTable(device_ip=ip, metric=metric)
            state.state = "ok"
            state.consecutive_checks = consecutive_checks
            self.session.add(state)

        return state

    def update(self, state: AlertStateTable) -> None:
        """
        Update an alert state.

        Args:
            state (AlertStateTable): The updated instance of AlertStateTable class.
        """
        self.session.add(state)

    def fetch_alert_state(self, ip: str) -> tuple[str, str] | None:
        """
        Return current alert state for a given IP address.

        Args:
            ip (str): IP address to search for.

        Returns:
            tuple[str,str]: A tuple containing `metric` and `state`.
        """
        device_state = (
            self.session.query(AlertStateTable).filter_by(device_ip=ip).one_or_none()
        )
        if device_state is None:
            return None
        return (device_state.metric, device_state.state)
