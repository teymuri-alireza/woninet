from sqlalchemy.orm import Session
from woninet.database.tables import AlertEventTable


class AlertEventRepository:
    """
    Repository for presisting Alert Event entries.

    Encapsulate ORM operations on `AlertEventTable`.
    """

    def __init__(self, session: Session) -> None:
        """
        Initialize the repository.

        Args:
            session (Session): SQLAlchemy session used for all database operations.
        """
        self.session = session

    def insert(self, event: AlertEventTable) -> None:
        """
        Insert new alert event in the database.

        Args:
            event (AlertEvent): Instance of the AlertEventTable class.
        """
        self.session.add(event)

    def fetch_recent_device_alert_events(
        self, ip: str, limit: int = 10
    ) -> list[AlertEventTable]:
        """
        Returns the last 10 alert events of a device for a given IP address.

        Args:
            ip (str): IP address to search for.
            limit (int): Apply a limit to search.

        Returns:
            list[AlertEventTable]: List of found event, or an empty list if found none.
        """
        return (
            self.session.query(AlertEventTable)
            .filter_by(device_ip=ip)
            .order_by(AlertEventTable.id.desc())
            .limit(limit)
            .all()
        )
