from woninet.core.models import Device, MetricRecord
from woninet.database.tables import AlertStateTable, AlertEventTable
from woninet.database.repositories.device_repository import DeviceRepository
from woninet.database.repositories.metric_repository import MetricRepository
from woninet.database.repositories.alert_state_repository import AlertStateRepository
from woninet.database.repositories.alert_event_repository import AlertEventRepository


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

    def list_device_history(self) -> list[Device]:
        """
        Return all stored devices in the database.

        Returns:
            list[Device]: list devices retrieved from the database.
        """
        with self.session_factory() as session:
            repo = DeviceRepository(session)
            return repo.fetch_devices()

    def fetch_device_info(self, ip) -> Device | None:
        """
        Return a device from the database for the given IP address or
        `None` if not found.
        """
        with self.session_factory() as session:
            repo = DeviceRepository(session)
            return repo.fetch_device(ip)

    def count_devices_and_metrics(self) -> tuple[int, int]:
        """
        Return number of devices and metrics in the database.

        Returns:
            tuple[int,int]: Number of devices and metrics in the database.
        """
        with self.session_factory() as session:
            device_repo = DeviceRepository(session)
            metric_repo = MetricRepository(session)
            return (
                device_repo.count_devices(),
                metric_repo.count_metrics(),
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

    def list_metric_history(self) -> list[MetricRecord]:
        """
        Return stored metric history.

        Returns:
            list[MetricRecord]: Metric records retrieved from the database.
        """
        with self.session_factory() as session:
            repo = MetricRepository(session)
            return repo.fetch_metrics()

    def get_or_create_alert_state(self, ip: str, metric: str) -> AlertStateTable:
        """
        Return the alert state for a given IP address and metric.

        Returns:
            AlertStateTable: The found alert state.
        """
        with self.session_factory() as session:
            repo = AlertStateRepository(session=session)
            return repo.fetch_or_create_alert_state(ip=ip, metric=metric)

    def update_alert_state(self, state: AlertStateTable) -> None:
        """
        Update an alert state.

        Args:
            state (AlertStateTable): The updated instance of AlertStateTable class.
        """
        with self.session_factory() as session:
            repo = AlertStateRepository(session=session)
            repo.update(state=state)
            session.commit()

    def get_device_alert_state(self, ip: str) -> tuple[str, str] | None:
        """
        Return alert state of a device for a given IP address.
        """
        with self.session_factory() as session:
            repo = AlertStateRepository(session)
            return repo.fetch_alert_state(ip=ip)

    def store_alert_event(self, event: AlertEventTable) -> None:
        """
        Store the new alert event.

        Args:
            event (AlertEvent): Instance of the AlertEventTable class.
        """
        with self.session_factory() as session:
            repo = AlertEventRepository(session=session)
            repo.insert(event=event)
            session.commit()

    def get_recent_alert_events(self) -> list[AlertEventTable]:
        """
        Return recent alert events of all devices.
        """
        with self.session_factory() as session:
            repo = AlertEventRepository(session)
            return repo.fetch_recent_alert_events()

    def get_recent_device_alert_events(self, ip: str) -> list[AlertEventTable]:
        """
        Return recent alert events of a device for a given IP address.
        """
        with self.session_factory() as session:
            repo = AlertEventRepository(session=session)
            return repo.fetch_recent_device_alert_events(ip=ip)
