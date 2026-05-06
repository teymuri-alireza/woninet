from woninet.core.models import Device
from woninet.core.models import MetricRecord
from woninet.database.repositories.device_repository import DeviceRepository
from woninet.database.repositories.metric_repository import MetricRepository


class StorageEngine:
    """
    Provide a high-level API for storing, updating, and
    retrieving data from the database.

    Also manage database sessions and delegate persistence
    operations to repository classes.
    """

    def __init__(self, session_factory) -> None:
        """
        Initialize the storage engine.

        Args:
            session_factory (SessionLocal): Factory responsible for creating SQLAlchemy sessions.
        """
        self.session_factory = session_factory

    def store(self, device: Device) -> None:
        """
        Insert or update a collected device.

        Args:
            device (Device): Device instance to be persisted.
        """
        with self.session_factory() as session:
            repo = DeviceRepository(session)
            repo.upsert(device)
            session.commit()

    def get_history(self) -> list[Device]:
        """
        Return all stored devices in the database.

        Returns:
            list[Device]: list devices retrieved from the database.
        """
        with self.session_factory() as session:
            repo = DeviceRepository(session)
            return repo.get_db_devices()

    def get_database_count(self) -> tuple[int, int]:
        """
        Return number of devices and metrics in the database.

        Returns:
            tuple[int,int]: Number of devices and metrics in the database.
        """
        with self.session_factory() as session:
            device_repo = DeviceRepository(session)
            metric_repo = MetricRepository(session)
            return (
                device_repo.get_db_devices_count(),
                metric_repo.get_db_metrics_count(),
            )

    def store_metric(self, metric: MetricRecord) -> None:
        """
        Persist newly collected metric record.

        Args:
            metric (MetricRecord): A metric record captured during a scan cycle.
        """
        with self.session_factory() as session:
            repo = MetricRepository(session)
            repo.insert(metric)
            session.commit()

    def get_metric_history(self) -> list[MetricRecord]:
        """
        Return stored metric history.

        Returns:
            list[MetricRecord]: Metric records retrieved from the database.
        """
        with self.session_factory() as session:
            repo = MetricRepository(session)
            return repo.get_db_metrics()

    def clear_metric_history(self) -> None:
        """
        Remove all stored metric history from the database.
        """
        with self.session_factory() as session:
            repo = MetricRepository(session)
            repo.remove_db_metrics()
            session.commit()
