from datetime import datetime
from sqlalchemy.orm import Session
from woninet.database.tables import MetricTable
from woninet.core.models import MetricRecord


class MetricRepository:
    """
    Repository for persisting and retrieving MetricRevord entities.

    Encapsulate OEM operations on `MetricTable` and expose a
    simple API in terms of the domain model `MetricRecord`.
    """

    def __init__(self, session: Session) -> None:
        """
        Initialize the repository.

        Args:
            session (Session): SQLAlchemy session used for all database operations.
        """
        self.session: Session = session

    def insert(self, metric: MetricRecord) -> None:
        """
        Insert new metric in the database.

        Args:
            metric (MetricRecord): An object of domain `MetricRecord` instance.
        """
        self.session.add(
            MetricTable(
                device_ip=metric.device_ip,
                metric=metric.metric,
                value=metric.value,
                timestamp=metric.timestamp or datetime.now(),
            )
        )
        self.session.commit()

    def get_db_metrics(self) -> list[MetricRecord]:
        """
        Return all metric records from database.

        Returns:
            list[MetricRecord]: A list of `MetricRecord` instances from `MetricTable` in the database.
        """
        rows = self.session.query(MetricTable).all()
        result = []
        for row in rows:
            metric = MetricTable(
                device_ip=row.device_ip, metric=row.metric, value=row.value
            )
            result.append(metric)
        return result

    def remove_db_metrics(self) -> None:
        """
        Remove all rows from the `MetricTable`.
        """
        self.session.query(MetricTable).delete()
        self.session.commit()

    def get_db_metrics_count(self) -> int:
        """
        Return the number of metrics in the database.

        Returns:
            int: Number of metrics in the database.
        """
        total = self.session.query(MetricTable).count()
        return total
