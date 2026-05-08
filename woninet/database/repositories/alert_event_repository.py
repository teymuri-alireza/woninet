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
