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

    def fetch_alert_state(self, ip: str, metric: str) -> AlertStateTable:
        """
        Return an alert state for a specfic IP address and metric; Create a new one
        if it already doesn't exist.

        Args:
            ip (str): IP address of host.
            metric (str): Name of the metric beaing monitored.

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
            self.session.add(state)

        return state

    def update(self, state: AlertStateTable) -> None:
        """
        Update an alert state.

        Args:
            state (AlertStateTable): The updated instance of AlertStateTable class.
        """
        self.session.add(state)
